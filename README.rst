=====================
azureenergylabelercli
=====================

A cli to help generate energy label for Azure tenant, subscriptions and resource groups. 


* Documentation: https://azureenergylabelercli.readthedocs.org/en/latest


Energy Labels
=============

.. csv-table:: Energy Labels table
  :header: "label", "high", "medium", "low"

  "A =>", "0", "up to 10", "up to 20"
  "B ==>", "up to 10", "up to 20", "up to 40"
  "C ===>", "up to 15", "up to 30", "up to 60"
  "D ====>", "up to 20", "up to 40", "up to 80"
  "E =====>", "up to 25", "up to 50", "up to 100"


Arguments
=========

.. csv-table:: CLI Arguments table
  :header: "description", "CLI argument", "environment variable", "example value"

  "Tenand ID (required)", "`--tenant-id`", "`AZURE_LABELER_TENANT_ID`", "`00000000-0000-0000-0000-000000000000`"
  "Path to export the results", "`--export-path`", "`AZURE_LABELER_EXPORT_PATH`", "`/local/path` or Storage Account Url with SAS token `https://sa.blob.windows.net/container/?sas_token`"
  "Export only number of findings and energy label", "`--export-metrics`", "`AZURE_LABELER_EXPORT_METRICS`", "`false` (default)"
  "Export all findings information along with energy label", "`--export-all`", "`AZURE_LABELER_EXPORT_ALL`", "`true` (default)"
  "Regulatory frameworks to take into account", "`--frameworks`", "`AZURE_LABELER_FRAMEWORKS`", "`'Azure Security Benchmark,Azure CIS 1.1.0'`"
  "Explicit list of subscriptions to take into account", "`--allowed-subscription-ids`", "`AZURE_LABELER_TENANT_ID`", "`'00000000-0000-0000-0000-000000000000,00000000-0000-0000-0000-000000000001'`"
  "Explicit list of subscriptions NOT to take into account", "`--denied-subscription-ids`", "`AZURE_LABELER_DENIED_SUBSCRIPTION_IDS`", "`'00000000-0000-0000-0000-000000000000,00000000-0000-0000-0000-000000000001'`"
  "Level of log printing", "`--log-level`", "`AZURE_LABELER_LOG_LEVEL`", "`info`"
  "Logging configuration", "`--log-config`", "`AZURE_LABELER_LOG_CONFIG`", ""


Supported authentication types
==============================

Azure CLI
---------

If you are running the Energy Labeler from your local machine, make sure the user you are authenticated as has the `Security Reader` permission or higher.

.. code-block:: bash
 
  az login --tenant 00000000-0000-0000-0000-000000000000

Managed Identity
----------------

If you are running the `azureenergylabeler` container in Azure (on ACI, ACA, etc), this is safest and preferred authentication method. 
To make use of Managed Identity authentication for the Energy Labeler, make sure it is enabled on your instance (ACI, Function App, etc):
.. code-block::

  identity: {
      type: 'SystemAssigned'
          
  }


Also make sure you have a role assignment to your instance, `Security Reader` is required.
.. code-block::

  @description('Security Reader role definition')
  var roleDefinitionId = resourceId('microsoft.authorization/roleDefinitions', '39bc4728-0917-49c7-9d2c-d95423bc2eb4')
  
  @description('Assign Security Reader role to the container so it can gather security compliance of the subscription/tenant')
  resource securityReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(name)
    scope: tenant()
    properties: {
      principalId: containergroup.identity.principalId
      roleDefinitionId: roleDefinitionId
    }
  }

Service Principal credentials
-----------------------------

If you are running the `azureenergylabeler` container outside Azure, you need to authenticate to Azure using Service Principal credentials.
The Service Principal therefore must have `Security Reader` permission assigned to either at Tenant Level or to the subscriptions where Energy Label are calculated.

Service principal with secret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: CLI Arguments table
  :header: "variable name", "value"

  "`AZURE_CLIENT_ID`", "id of an Azure Active Directory application"
  "`AZURE_TENANT_ID`", "id of the application's Azure Active Directory tenant"
  "`AZURE_CLIENT_SECRET`", "one of the application's client secrets"

Service principal with certificate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: CLI Arguments table
  :header: "variable name", "value"

  "`AZURE_CLIENT_ID`", "id of an Azure Active Directory application"
  "`AZURE_TENANT_ID`", "id of the application's Azure Active Directory tenant"
  "`AZURE_CLIENT_CERTIFICATE_PATH`", "path to a PEM or PKCS12 certificate file including private key"
  "`AZURE_CLIENT_CERTIFICATE_PASSWORD`", "password of the certificate file, if any"


Installation
============

Pipx
----

.. code-block::

  pipx install azureenergylabelercli
    installed package azureenergylabelercli 1.0.0, installed using Python 3.10.5
    These apps are now globally available
      - azure-energy-labeler
      - azure_energy_labeler_cli.py
  done! ✨ 🌟 ✨


Examples
========

Calculate energy label for a tenant
-----------------------------------

.. code-block::

  azure-energy-labeler --tenant-id <TENANT_ID>

Calculate energy label for two subscriptions in a tenant
--------------------------------------------------------

.. code-block::

  azure-energy-labeler --tenant-id <TENANT_ID> --allowed-subscription-ids 00000000-0000-0000-0000-000000000000,00000000-0000-0000-0000-000000000001


Calculate energy label for a tenant and export all findings to a local folder
-----------------------------------------------------------------------------

.. code-block::

  azure-energy-labeler --tenant-id 2ba489e8-3466-4f52-a32d-263d28b832e1 --export-path /tmp/ --export-all


Calculate energy label for a tenant and export all findings to a Storage Account Blob Container
-----------------------------------------------------------------------------------------------

.. code-block::

  azure-energy-labeler --tenant-id 2ba489e8-3466-4f52-a32d-263d28b832e1 --export-path "https://sa.blob.windows.net/container/?sas_token" --export-all
