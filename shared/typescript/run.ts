// CLI and resumable execution. Copy alongside meshy.ts.
import { createHash } from "node:crypto";
import { mkdir, open, readFile, readdir, rename, stat, unlink, writeFile } from "node:fs/promises";
import { basename, extname, join, resolve } from "node:path";
import { parseArgs } from "node:util";
import { Meshy, type Task } from "./meshy.js";

export interface Options { input: string[]; prompt: string; output: string; dryRun: boolean; resume: boolean }

export async function argumentsFor(directory: string, description: string, defaults: { images?: string[]; prompt?: string }): Promise<Options> {
  const { values } = parseArgs({ options: {
    ...(defaults.images ? { input: { type: "string" as const, multiple: true } } : {}),
    ...(defaults.prompt !== undefined ? { prompt: { type: "string" as const } } : {}),
    output: { type: "string" }, "dry-run": { type: "boolean" }, resume: { type: "boolean" }, help: { type: "boolean", short: "h" },
  } });
  if (values.help) {
    console.log(`${description}\n${defaults.images ? "--input PATH (repeat for photos, front first)\n" : "--prompt TEXT\n"}--output DIR\n--dry-run (offline; no writes)\n--resume (reuse saved task IDs)`);
    process.exit(0);
  }
  const args: Options = { input: ((values.input as string[] | undefined) ?? defaults.images ?? []).map(p => resolve(p)),
    prompt: (values.prompt as string | undefined) ?? defaults.prompt ?? "", output: resolve((values.output as string | undefined) ?? join(directory, "output")),
    dryRun: Boolean(values["dry-run"]), resume: Boolean(values.resume) };
  if (args.dryRun && args.resume) throw new Error("--dry-run and --resume cannot be combined");
  if (defaults.images) {
    const maximum = defaults.images.length === 1 ? 1 : 4;
    if (args.input.length < 1 || args.input.length > maximum) throw new Error(`Expected 1 to ${maximum} input images`);
    for (const path of args.input) {
      const data = await readFile(path);
      const extension = extname(path).toLowerCase();
      if (!((extension === ".png" && data.subarray(0, 8).equals(Buffer.from("89504e470d0a1a0a", "hex"))) ||
            ([".jpg", ".jpeg"].includes(extension) && data.subarray(0, 3).equals(Buffer.from("ffd8ff", "hex")))))
        throw new Error(`Expected a PNG or JPEG with a matching extension: ${path}`);
    }
  }
  if (defaults.prompt !== undefined && !args.prompt.trim()) throw new Error("--prompt must not be empty");
  return args;
}

const hash = (data: string | Buffer) => createHash("sha256").update(data).digest("hex");
function sorted(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sorted);
  if (value !== null && typeof value === "object") return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([k, v]) => [k, sorted(v)]));
  return value;
}
function summarize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(summarize);
  if (value !== null && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, summarize(v)]));
  return typeof value === "string" && value.startsWith("data:") ? value.split(",")[0] + ",<omitted>" : value;
}
async function exists(path: string) {
  try { await stat(path); return true; } catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") return false; throw error; }
}
export async function validateGlb(path: string) {
  const file = await open(path, "r");
  try {
    const header = Buffer.alloc(12);
    const { bytesRead } = await file.read(header, 0, 12, 0);
    if (bytesRead !== 12 || header.toString("ascii", 0, 4) !== "glTF" || header.readUInt32LE(4) !== 2 || header.readUInt32LE(8) !== (await file.stat()).size)
      throw new Error(`Invalid GLB v2 header or length: ${path}`);
  } finally { await file.close(); }
}

interface SavedTask { endpoint: string; payload_sha256: string; status: string; requested_model: string; id?: string; consumed_credits?: number; reported_model?: string }
interface Artifact { path: string; bytes: number; sha256: string; validation: string }
interface State { schema_version: number; recipe: string; status: string; tasks: Record<string, SavedTask>; artifacts: Record<string, Artifact>; consumed_credits: number; configuration?: unknown }

export class Run {
  private client?: Meshy;
  private state: State;
  private plan: unknown[] = [];
  readonly path: string;
  constructor(private recipe: string, private args: Options, private directory: string, private estimatedCredits: number) {
    this.path = join(args.output, "result.json");
    this.state = { schema_version: 1, recipe, status: "RUNNING", tasks: {}, artifacts: {}, consumed_credits: 0 };
  }
  private async save() {
    const temporary = join(this.args.output, "result.json.tmp");
    await writeFile(temporary, JSON.stringify(this.state, null, 2) + "\n");
    await rename(temporary, this.path);
  }
  async execute(workflow: (run: Run) => Promise<void>) {
    if (this.args.dryRun) {
      await workflow(this);
      console.log(JSON.stringify({ mode: "dry-run", recipe: this.recipe, estimated_credits: this.estimatedCredits, output: this.args.output, steps: this.plan }, null, 2));
      return;
    }
    await mkdir(this.args.output, { recursive: true });
    const lock = join(this.args.output, ".run.lock");
    let handle;
    try { handle = await open(lock, "wx"); }
    catch (error) { if ((error as NodeJS.ErrnoException).code === "EEXIST") throw new Error(`Run locked: ${lock}. See RUNNING.md before removing a stale lock.`); throw error; }
    try {
      await handle.close();
      const configuration = { prompt: this.args.prompt || null, input_sha256: await Promise.all(this.args.input.map(async p => hash(await readFile(p)))) };
      if (this.args.resume) {
        this.state = JSON.parse(await readFile(this.path, "utf8"));
        if (this.state.schema_version !== 1 || this.state.recipe !== this.recipe) throw new Error("Saved run has a different recipe or unsupported schema");
        if (JSON.stringify(sorted(this.state.configuration)) !== JSON.stringify(sorted(configuration))) throw new Error("Inputs changed. Repeat the original flags or use a new --output directory.");
        if (this.state.status === "SUCCEEDED" && Object.keys(this.state.artifacts).length && (await Promise.all(Object.entries(this.state.artifacts).map(async ([name, saved]) => {
          const path = join(this.args.output, name);
          return await exists(path) && hash(await readFile(path)) === saved.sha256;
        }))).every(Boolean)) {
          console.log(`Already complete: ${this.path}  (${this.state.consumed_credits} credits)`);
          return;
        }
      } else if (await exists(this.path)) throw new Error("This output already has a run. Use --resume or a new --output directory.");
      if (!this.args.resume && (await readdir(this.args.output)).some(name => ![".run.lock", ".gitkeep", ".DS_Store"].includes(name))) throw new Error("Output directory contains files without a saved run. Use a new --output directory.");
      this.state.configuration = configuration;
      this.state.status = "RUNNING";
      await this.save();
      console.log(`Estimated full-run cost: ~${this.estimatedCredits} credits; resuming reuses saved task IDs.`);
      try {
        await workflow(this);
        this.state.status = "SUCCEEDED";
        await this.save();
        console.log(`Done: ${this.path}  (${this.state.consumed_credits} credits)`);
      } catch (error) { this.state.status = "ERROR"; await this.save(); throw error; }
    } finally { await unlink(lock); }
  }
  private api() { return this.client ??= new Meshy(undefined, join(this.directory, ".env")); }
  async task(label: string, endpoint: string, payload: Record<string, unknown>): Promise<Task> {
    if (this.args.dryRun) {
      this.plan.push({ stage: label, endpoint, payload: summarize(payload) });
      return { id: `<saved-${label}-id>`, status: "SUCCEEDED", progress: 100, consumed_credits: 0,
        model_urls: { glb: "<glb-url>", usdz: "<usdz-url>" }, image_urls: ["<image-url>"], thumbnail_url: "<thumbnail-url>",
        thumbnail_urls: { front: "<front-url>", right: "<right-url>", back: "<back-url>", left: "<left-url>" } };
    }
    const fingerprint = hash(JSON.stringify(sorted(payload)));
    let saved = this.state.tasks[label];
    if (saved) {
      if (saved.endpoint !== endpoint || saved.payload_sha256 !== fingerprint) throw new Error(`Inputs or parameters changed for ${label}. Use a new --output directory.`);
      if (!saved.id) throw new Error(`Submission outcome unknown for ${label}; reconcile the task in Meshy before retrying. See RUNNING.md.`);
    } else {
      const client = this.api();
      saved = { endpoint, payload_sha256: fingerprint, status: "SUBMITTING", requested_model: String(payload.ai_model ?? "latest") };
      this.state.tasks[label] = saved;
      await this.save();
      saved.id = await client.create(endpoint, payload);
      saved.status = "PENDING";
      await this.save();
    }
    let task: Task;
    try { task = await this.api().wait(endpoint, saved.id!, label); }
    catch (error) {
      if (error && typeof error === "object" && "task" in error) { saved.status = (error.task as Task).status; await this.save(); }
      throw error;
    }
    saved.status = task.status;
    saved.consumed_credits = task.consumed_credits ?? 0;
    if (task.ai_model) saved.reported_model = task.ai_model;
    this.state.consumed_credits = Object.values(this.state.tasks).reduce((sum, t) => sum + (t.consumed_credits ?? 0), 0);
    await this.save();
    return task;
  }
  async download(url: string, filename: string) {
    if (basename(filename) !== filename) throw new Error("Artifact name must be a filename");
    const dest = join(this.args.output, filename);
    if (this.args.dryRun) { this.plan.push({ artifact: dest }); return dest; }
    const saved = this.state.artifacts[filename];
    if (saved && await exists(dest) && hash(await readFile(dest)) === saved.sha256) return dest;
    const partial = dest + ".part";
    await this.api().download(url, partial);
    if (!(await stat(partial)).size) throw new Error(`Empty download: ${filename}`);
    if (extname(dest) === ".glb") await validateGlb(partial);
    await rename(partial, dest);
    this.state.artifacts[filename] = { path: dest, bytes: (await stat(dest)).size, sha256: hash(await readFile(dest)), validation: extname(dest) === ".glb" ? "glb-header" : "nonempty" };
    await this.save();
    return dest;
  }
}
