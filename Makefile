PREFIX="sdx-"
REPOS="concourse" "helm" "terraform" "tester" "worker"
SDX_GCP_DIR=""#enter the name of hte directory where you have put your sdx-gcp repos
update:
	@ printf "\n[${YELLOW} Updating/Cloning repos in ${SDX_HOME}${SDX_GCP_DIR} ${NO_COLOR}]\n"
	@ for r in ${REPOS}; do \
		echo "(${PREFIX}$${r})"; \
		if [ ! -e ${SDX_HOME}/${PREFIX}$${r} ]; then \
			git clone git@github.com:ONSdigital/${PREFIX}$${r}.git ${SDX_HOME}/${PREFIX}$${r}; \
		else \
			cd ${SDX_HOME}/${PREFIX}$${r}; \
			echo "On branch [`git symbolic-ref --short HEAD`], updating repo..."; \
			git pull; cd; \
		fi; echo ""; \
	done
