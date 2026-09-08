#!/bin/bash

# flow from inference to proposal

session_id=$(python trainer/inference_agent.py --task_id 1234455 --task_name development-task --query "Current realtime weather in Hamburg Germany please" --system_prompt "Answer user question and finish task. Your answers must be based on true and reality, avoid answering that you do not know" --skills_dir ./workspace/skills --output_dir ./output --stream_mode | tail -n 1)

echo $session_id

python trainer/wiki_maintainer.py --traces_dir ./output/$session_id/1234455 --wiki_dir ./workspace/wiki --stream_mode

python trainer/skill_proposer.py --session_id $session_id --task_id 1234455 --traces_dir ./output/$session_id/1234455 --workspace_dir ./workspace --output_dir ./output --stream_mode