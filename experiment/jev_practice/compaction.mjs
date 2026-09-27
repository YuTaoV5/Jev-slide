// Runs the actual upstream library with explicit, artificial decision fixtures.
import { compact, reductionRatio } from '../../related_work/projects/fast-jev-compaction-main/dist/index.js';
import { writeFileSync, mkdirSync } from 'node:fs';
import assert from 'node:assert/strict';
const out = new URL('./results/', import.meta.url);
mkdirSync(out, { recursive: true });
const messages = [{role:'user', text:'修复登录测试；不要编辑 generated 目录。', toolUses:[]}];
const samples = [
  ['old-search','Search',{query:'旧版登录入口'},'旧搜索结果（已失效）\n'.repeat(420)],
  ['read-file','Read',{file_path:'src/login.ts'},'源代码内容，可重新读取\n'.repeat(280)],
  ['error','Test',{command:'test login'},'唯一错误证据：expected 401, got 200'],
  ['recent','Read',{file_path:'src/current.ts'},'最近读取结果，固定保留'],
];
for (const [id,tool,input,result] of samples) {
  messages.push({role:'assistant',text:'',toolUses:[{tool_use_id:id,tool,input}]});
  messages.push({role:'user',text:'',toolUses:[],toolResults:[{tool_use_id:id,text:result}]});
}
const pairs = {t1:[0.1,0.05],t2:[0.9,0.1],t3:[0.95,0.95]};
const requests=[];
const asker={async ask(state,questions){
  requests.push({state,questions});
  return {answers:Object.fromEntries(Object.keys(questions).map(key=>{
    const [kind,id]=key.split('_');
    assert.ok(pairs[id],`Unexpected fixture id ${id}`);
    return [key,{noul:pairs[id][kind==='call'?0:1]}];
  }))};
}};
const options={preserveRecentMessages:2,keepThreshold:0.5,truncateHeadChars:80};
const result=await compact(messages,asker,options);
assert.deepEqual(result.decisions.map(x=>x.action),['drop_call','drop_result','keep','keep']);
assert.equal(result.messages[0].text,messages[0].text);
const ids=new Set(result.messages.flatMap(m=>m.toolUses.map(t=>t.tool_use_id)));
for(const m of result.messages) for(const r of m.toolResults??[]) assert.ok(ids.has(r.tool_use_id));
assert.ok(result.messages.some(m=>m.toolResults?.some(r=>r.text==='唯一错误证据：expected 401, got 200')));
await assert.rejects(compact(messages,{async ask(){return {answers:{}}}},options));
const report={mode:'offline-fixture',model:null,api_calls:0,cost_usd:0,seed:null,
  timestamp:new Date().toISOString(),runtime:process.version,options,fixture_probabilities:pairs,
  input:messages,requests,...result,reduction_ratio:reductionRatio(result),
  limitation:'Artificial probabilities; character reduction is not a measured token, cost, or accuracy improvement.'};
writeFileSync(new URL('compaction.json',out),JSON.stringify(report,null,2));
console.log(JSON.stringify({mode:report.mode,...result.stats,reduction_ratio:report.reduction_ratio}));
