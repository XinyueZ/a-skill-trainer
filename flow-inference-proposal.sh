#!/bin/bash

# run: ./flow-inference-proposal.sh --task_id 1 --task_name "flow-inference-proposal" --query "Current realtime weather in Hamburg Germany please"
echo "🏃‍♂️  Flow from inference to proposal"

TASK_ID=1
TASK_NAME="default_name"
QUERY="Current realtime weather in Hamburg Germany please"

while [[ $# -gt 0 ]]; do
  case $1 in
    --task_id)
      TASK_ID="$2"
      shift 2
      ;;
    --task_name)
      TASK_NAME="$2"
      shift 2
      ;;
    --query)
      QUERY="$2"
      shift 2
      ;;
    *)
      echo "❌ 未知参数: $1"
      exit 1
      ;;
  esac
done


if ! [[ "$TASK_ID" =~ ^[0-9]+$ ]]; then
    echo "❌ A number for task_id is required: $TASK_ID"
    exit 1
fi

if [ -z "$TASK_NAME" ]; then
    echo "❌ A string for task_name is required: $TASK_NAME"
    exit 1
fi

if [ -z "$QUERY" ]; then
    echo "❌ A string for query is required: $QUERY"
    exit 1
fi

echo "✅ Task ID: $TASK_ID"
echo "✅ Task Name: $TASK_NAME"
echo "✅ Query: $QUERY"

session_id=$(python trainer/inference_agent.py --task_id $TASK_ID --task_name $TASK_NAME --query "$QUERY" --system_prompt "Answer user question and finish task. Your answers must be based on true and reality, avoid answering that you do not know" --skills_dir ./workspace/skills --output_dir ./output --stream_mode | tail -n 1)
echo "$session_id" > ./output/latest_session.txt

python trainer/wiki_maintainer.py --traces_dir ./output/$session_id/$TASK_ID --wiki_dir ./workspace/wiki --stream_mode

python trainer/skill_proposer.py --session_id $session_id --task_id $TASK_ID --traces_dir ./output/$session_id/$TASK_ID --workspace_dir ./workspace --output_dir ./output --stream_mode