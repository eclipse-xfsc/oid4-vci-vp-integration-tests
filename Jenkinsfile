pipeline {
    agent {
        kubernetes {
            defaultContainer "python"
            // language=yaml
            yaml """
---
apiVersion: v1
kind: Pod

spec:
  restartPolicy: Never
   
  hostAliases: # this is a placeholder, to be updated when domain available
  - ip: "10.111.252.111"
    hostnames:
    - "tcr.train1.xfsc.dev" 
    - "tspa.train1.xfsc.dev"
    - "zonemgr.train1.xfsc.dev"
  containers:
    - name: python
      
      # see `make docker-build-python-with-podman`  how to build it, TODO: build and push with GitlabCI
      image: "node-654e3bca7fbeeed18f81d7c7.ps-xaas.io/train/bdd/python_with_podman_v2:3.11" 
      
      command:
        - cat
      tty: true
      securityContext:
        privileged: true
      volumeMounts:
        - mountPath: /var/lib/containers
          name: podman-volume
        - mountPath: /dev/shm
          name: dev-shm-volume
        - mountPath: /var/run
          name: var-run-volume
        - mountPath: /tmp
          name: tmp-volume
  volumes:
    - name: podman-volume
      emptyDir: {}
    - name: dev-shm-volume
      emptyDir:
        medium: Memory
    - name: var-run-volume
      emptyDir: {}
    - name: tmp-volume
      emptyDir: {}
"""
        }
    }
    environment {
        EU_XFSC_BDD_CORE_PATH = "${WORKSPACE}/eclipse/xfsc/dev-ops/testing/bdd-executor"

        SOURCE_PATHS = "src"
        VENV_PATH_DEV = "${WORKSPACE}/.cache/.venv"
        PYLINTHOME = "${WORKSPACE}/.cache/pylint"
        PIP_CACHE_DIR = "${WORKSPACE}/.cache/pip"
        DOCKER = "podman"
    }

    stages {
        stage('Clone sources') {
            steps {
                // language=sh
                sh """#!/bin/bash
                set -x -eu -o pipefail
                
                mkdir -p "${EU_XFSC_BDD_CORE_PATH}/.."
                cd "${EU_XFSC_BDD_CORE_PATH}/.."

                git clone https://gitlab.eclipse.org/eclipse/xfsc/dev-ops/testing/bdd-executor.git \
                  -b 1-bdd-framework-migrate-train-bdd-testkit-2
                """
            }
        }

        stage("Prepare cache folders") {
            steps {
                // language=sh
                sh """#!/bin/bash
                set -x -eu -o pipefail
                
                mkdir -p "${PYLINTHOME}/"
                mkdir -p "${PIP_CACHE_DIR}/"
                """
            }
        }

        stage("Build") {
            steps {
                // language=sh
                sh """#!/bin/bash
                set -x -eu -o pipefail

                make setup_dev
                """
            }
        }

        stage("Test") {
            parallel {
                stage("isort") {
                    steps {
                        // language=sh
                        sh """#!/bin/bash
                        make isort
                        """
                    }
                }
                stage("pylint") {
                    steps {
                        // language=sh
                        sh """#!/bin/bash
                        set -x -eu -o pipefail
                        
                        export ARG_PYLINT_JUNIT="--output-format=junit"
                        make pylint > ".tmp/pylint.xml" 
                        """
                    }
                    post {
                        always {
                            recordIssues \
                                enabledForFailure: true,
                                aggregatingResults: true,
                                tool: pyLint(pattern: ".tmp/pylint.xml")
                        }
                    }
                }
                stage("coverage") {
                    steps {
                        // language=sh
                        sh """#!/bin/bash
                        set -x -eu -o pipefail
                        
                        export ARG_COVERAGE_PYTEST=--junit-xml=".tmp/pytest.xml"
                        make coverage_run coverage_report
                        """
                    }
                    post {
                        always {
                            junit ".tmp/pytest.xml"
                        }
                    }
                }
                stage("mypy") {
                    steps {
                        // language=sh
                        sh """#!/bin/bash
                        set -x -eu -o pipefail
                        
                        export ARG_MYPY_SOURCE_XML="--junit-xml='.tmp/mypy-source.xml'"
                        make mypy
                        """
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tools: [myPy(pattern: ".tmp/mypy*.xml")]
                        }
                    }
                }
                stage("THIRD-PARTY.txt") {
                    steps {
                        // language=sh
                        sh """#!/bin/bash
                        set -x -eu -o pipefail
                        
                        # third-party-license-file-generator
                        """
                    }
                }

                stage("Run bdd test on ocm") {
                    steps {
                        // language=sh
                        sh """#!/bin/bash
                        set -x -eu -o pipefail
                        
                        mkdir -p ".tmp/behave/"

                        make run_bdd_dev
                        """
                    }
                }
            }
        }

        stage("Deliver reports") {
            steps {
                // language=sh
                sh """#!/bin/bash
                echo "doing delivery stuff.."
                """
            }
        }
    }
}