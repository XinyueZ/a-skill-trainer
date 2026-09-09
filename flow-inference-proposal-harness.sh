#!/bin/bash

# run: ./flow-inference-proposal-harness.sh --task_id 1 --task_name "walk-through-inference-proposal-harness" --query "Current realtime weather in Hamburg Germany please"
echo "🏃‍♂️  Walk through 5 rounds of flow-inference-proposal + harness"

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
 
# round 0
session_id=$(./flow-inference-proposal.sh --task_id $TASK_ID --task_name $TASK_NAME --query "$QUERY" | tail -n 1)
python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/$session_id/$TASK_ID/proposal.json  --reject --iteration 0 --feedback="It is better to use some scripts to support"

# round 1
session_id=$(./flow-inference-proposal.sh --task_id $TASK_ID --task_name $TASK_NAME --query "$QUERY" | tail -n 1)
python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/$session_id/$TASK_ID/proposal.json  --iteration 1 --feedback="Make the scripts more robust"

# round 2
session_id=$(./flow-inference-proposal.sh --task_id $TASK_ID --task_name $TASK_NAME --query "$QUERY" | tail -n 1)
python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/$session_id/$TASK_ID/proposal.json  --iteration 2 --feedback="Add reuqirments (libs strong versions) that the scripts can work with"

# round 3
session_id=$(./flow-inference-proposal.sh --task_id $TASK_ID --task_name $TASK_NAME --query "$QUERY" | tail -n 1)
python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/$session_id/$TASK_ID/proposal.json  --iteration 3 --reject --feedback="Enhance reuqirments(libs) installation descriptions and add more examples, potential errors or walkarounds"

# round 4
session_id=$(./flow-inference-proposal.sh --task_id $TASK_ID --task_name $TASK_NAME --query "$QUERY" | tail -n 1)
python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/$session_id/$TASK_ID/proposal.json  --iteration 4