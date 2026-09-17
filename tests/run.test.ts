import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { Meshy, type Task } from "../shared/typescript/meshy.js";
import { Run } from "../shared/typescript/run.js";

test("saved runs recover without duplicate generation", async () => {
  const directory = await mkdtemp(join(tmpdir(), "meshy-test-"));
  const original = { create: Meshy.prototype.create, wait: Meshy.prototype.wait, download: Meshy.prototype.download };
  const key = process.env.MESHY_API_KEY;
  process.env.MESHY_API_KEY = "offline-test";
  let creates = 0, waits = 0, downloads = 0;
  let failWait = false, failCreate = false, badDownload = false;
  Meshy.prototype.create = async () => { creates++; if (failCreate) throw new Error("POST response lost"); return String(creates); };
  Meshy.prototype.wait = async (_endpoint, id, label) => {
    waits++; if (failWait) throw new Error("Polling interrupted");
    return { id, status: "SUCCEEDED", consumed_credits: label === "concept" ? 9 : 35, model_urls: { glb: "fake-url" } } as Task;
  };
  Meshy.prototype.download = async (_url, dest) => {
    downloads++;
    const glb = Buffer.alloc(12); glb.write("glTF"); glb.writeUInt32LE(2, 4); glb.writeUInt32LE(12, 8);
    await writeFile(dest, badDownload ? Buffer.from("broken") : glb); return dest;
  };
  const pipeline = async (run: Run) => {
    const concept = await run.task("concept", "text-to-image", { prompt: "chair" });
    const task = await run.task("model", "image-to-3d", { input_task_id: concept.id });
    await run.download(task.model_urls.glb, "chair.glb");
  };
  const runFor = (folder: string, resume = false, prompt = "chair", dryRun = false) => new Run("test", { input: [], prompt, output: join(directory, folder), resume, dryRun }, directory, 44);
  const state = async (folder: string) => JSON.parse(await readFile(join(directory, folder, "result.json"), "utf8"));
  try {
    failWait = true;
    await assert.rejects(runFor("resume").execute(pipeline), /Polling interrupted/);
    assert.equal((await state("resume")).tasks.concept.id, "1");
    await assert.rejects(runFor("resume").execute(pipeline), /already has a run/);
    await assert.rejects(runFor("resume", true, "lamp").execute(pipeline), /Inputs changed/);
    await assert.rejects(runFor("resume", true).execute(async r => { await r.task("concept", "text-to-image", { prompt: "lamp" }); }), /parameters changed/);
    failWait = false;
    await runFor("resume", true).execute(pipeline);
    assert.equal(creates, 2); assert.equal((await state("resume")).consumed_credits, 44);
    const previousWaits = waits;
    await runFor("resume", true).execute(pipeline);
    assert.equal(waits, previousWaits); assert.equal(downloads, 1);
    await writeFile(join(directory, "resume", "chair.glb"), "damaged");
    await runFor("resume", true).execute(pipeline);
    assert.equal(downloads, 2); assert.equal(creates, 2);

    failCreate = true;
    await assert.rejects(runFor("ambiguous").execute(pipeline), /POST response lost/);
    await assert.rejects(runFor("ambiguous", true).execute(pipeline), /outcome unknown/);
    assert.equal(creates, 3);
    failCreate = false; badDownload = true;
    await assert.rejects(runFor("download").execute(pipeline), /Invalid GLB/);
    assert.deepEqual((await state("download")).artifacts, {});
    badDownload = false;
    await runFor("download", true).execute(pipeline);
    assert.equal(creates, 5); assert.equal((await state("download")).consumed_credits, 44);

    await assert.rejects(runFor("missing", true).execute(pipeline), /ENOENT/);
    await mkdir(join(directory, "locked"));
    await writeFile(join(directory, "locked", ".run.lock"), "");
    await assert.rejects(runFor("locked").execute(pipeline), /Run locked/);
    await runFor("dry", false, "chair", true).execute(pipeline);
    await assert.rejects(readFile(join(directory, "dry", "result.json")), /ENOENT/);
    assert.equal(creates, 5);
  } finally {
    Object.assign(Meshy.prototype, original);
    if (key === undefined) delete process.env.MESHY_API_KEY; else process.env.MESHY_API_KEY = key;
    await rm(directory, { recursive: true, force: true });
  }
});
