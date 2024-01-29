#!/bin/bash
GREEN='\033[0;32m'
NC='\033[0m'
echo "${GREEN}============ Starting deployment ============${NC}"

DEPLOY_BRANCH="v3.0.8"
START=`date +%s`

git add .
git commit -m ${START}
git push origin ${DEPLOY_BRANCH}

echo "\n${GREEN}✔ 🎉 Deployed successfully.${NC}\n"

