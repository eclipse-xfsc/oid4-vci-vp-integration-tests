#!/bin/sh

export VAULT_ADDR='http://vault:8200'
export VAULT_TOKEN='test'

# Enable the transit secrets engine at path tenant_space/
#vault secrets enable -path=tenant_space transit

curl --header "X-Vault-Token: test" --request POST --data '{"type":"transit"}' http://vault:8200/v1/sys/mounts/tenant_space


# Enable the transit secrets engine at path tenant_space/
#vault secrets enable -path=tenant_space transit


 # Check if the transit engine was enabled successfully
if curl --header "X-Vault-Token: test" --request GET vault:8200/v1/sys/mounts | grep -q "tenant_space/"; then
  echo "Transit secrets engine enabled at path tenant_space/"
else
  echo "Failed to enable transit secrets engine at path tenant_space/"
  exit 1
fi

KEY_DATA=$(cat /vault-scripts/signerkey.json)

# Send the payload to Vault using curl
curl --header "X-Vault-Token: test" \
     --request POST \
     --data "$KEY_DATA" \
     http://vault:8200/v1/tenant_space/restore/signerkey

echo "Vault keys initialized successfully"