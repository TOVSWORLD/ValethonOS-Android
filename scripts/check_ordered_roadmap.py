#!/usr/bin/env python3
"""Validate stable roadmap ordering/hierarchy/contracts; live status is on Project4."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GROUPS={'display-backlight','touch','gpu','internal-storage','wifi','bluetooth','audio','charging-thermal','suspend-wake','usb','sd','sensors','video-decode','cameras'}
def validate(plan):
 tasks=plan['tasks'];containers={c['issue']:c for c in plan['containers']};by={t['issue']:t for t in tasks}
 if len(by)!=len(tasks) or len({t['order'] for t in tasks})!=len(tasks):raise ValueError('Duplicate task or execution order')
 for c in containers.values():
  expected={'Epic':None,'Feature':'Epic','Phase':'Feature'}[c['level']]
  if expected and (c['parent'] not in containers or containers[c['parent']]['level']!=expected):raise ValueError('Broken container hierarchy')
 groups=[t['hardware_group'] for t in tasks if t['hardware_group']]
 if len(groups)!=14 or set(groups)!=GROUPS:raise ValueError('Hardware groups must be14 unique dedicated tasks')
 for t in tasks:
  if t['parent'] not in containers or containers[t['parent']]['level']!='Phase':raise ValueError('Task parent must be a Phase')
  if not t['goal'] or not t['steps'] or not t['acceptance']:raise ValueError('Missing executable work or acceptance')
  if t['hardware_group'] and ('device' not in t['acceptance'].lower() or len(t['steps'])<3):raise ValueError('Hardware task lacks device gate or staged work')
  for dep in t['depends_on']:
   if dep not in by or by[dep]['order']>=t['order']:raise ValueError('Dependency is missing, forward or cyclic')
  if t['order']>10 and not t['depends_on']:raise ValueError('Unrelated task bypasses predecessor')
 contract=plan['pr_contract']
 for key in ['primary_task_issue_required','one_primary_issue_per_pr','predecessor_gate_required','reorder_requires_documented_prerequisite','no_unrelated_blocker_bypass','exact_head_checks_before_merge','hardware_done_requires_actual_device_evidence','unsupported_is_not_a_hardware_pass']:
  if contract.get(key) is not True:raise ValueError('Required workflow contract missing: '+key)
 if contract.get('max_active_implementation_tasks')!=1:raise ValueError('Only one implementation task may be active')
 exceptions=[t for t in tasks if t['existing_work_exception']]
 if len(exceptions)!=1 or exceptions[0].get('primary_pr')!=436 or not exceptions[0].get('no_new_scope'):raise ValueError('In-flight exception must remain bounded to436')
 if not any('outcome must be GO' in c for c in by[347]['conditions']):raise ValueError('Closed NO-GO must not unblock physical entry')
 first=plan['first_critical_path_issue']
 if by[first]['kind']!='decision' or by[first]['order']!=10:raise ValueError('Critical path must start with the entry decision')
 execution=plan.get('test_execution',{});stages=execution.get('stages',[]);stage_by={s['id']:s for s in stages}
 if len(stage_by)!=len(stages) or not {'T0','T1','T2A','T2B','T2C','T3'}.issubset(stage_by):raise ValueError('Shared test stages missing or duplicated')
 if execution.get('major_exit_stage')!='T1':raise ValueError('First Android home must not wait for peripheral/release stages')
 for key in ['preserve_issue_acceptance','one_install_per_candidate_session','one_final_recovery_per_session','defer_final_recovery_until_session_end','record_unready_checkpoints_as_not_run']:
  if execution.get(key) is not True:raise ValueError('Shared-session contract missing: '+key)
 if execution.get('all_hardware_ready_required') is not False or execution.get('physical_action_authorized_by_plan') is not False:raise ValueError('Test grouping cannot require all hardware or authorize a physical action')
 if contract.get('shared_stage_runtime_coqualification') is not True:raise ValueError('Shared runtime evidence must not be blocked by serial physical tests')
 positions={s['id']:i for i,s in enumerate(stages)}
 for stage in stages:
  if not stage['checkpoints'] or not stage['issues'] or any(n not in by for n in stage['issues']):raise ValueError('Shared stage needs known issues and checkpoints')
  if any(dep not in positions or positions[dep]>=positions[stage['id']] for dep in stage['depends_on']):raise ValueError('Shared-stage dependency is forward or cyclic')
  if stage['required_for_first_android_home'] != (stage['id'] in ['T0','T1']):raise ValueError('Peripheral/release scope cannot block first Android home')
 if stage_by['T0']['kind']!='offline' or stage_by['T0']['owner_device_action'] is not False:raise ValueError('Offline candidate gate cannot request a tablet test')
 if stage_by['T2C'].get('additional_runtime_prerequisites')!=[335]:raise ValueError('Suspend tests require qualified power/thermal prerequisites')
 for task in tasks:
  expected=[stage['id'] for stage in stages if task['issue'] in stage['issues']]
  if task.get('test_stages')!=expected:raise ValueError('Task/shared-stage mapping differs')
  if task['hardware_group'] and not expected:raise ValueError('Hardware issue missing shared-stage checkpoint')
 return {'passed':True,'tasks':len(tasks),'hardware_groups':len(groups),'first_critical_path_issue':first,'max_active_implementation_tasks':1,'runtime_qualification_inferred':False,'shared_test_stages':len(stages),'first_home_exit_stage':execution['major_exit_stage']}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path,nargs='?',default=ROOT/'docs/development/ordered-roadmap.json');a=p.parse_args();print(json.dumps(validate(json.loads(a.path.read_text())),indent=2))
if __name__=='__main__':main()
