#!/bin/bash

# Naming according to https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming

# Please keep appname lowercase. 
appname="powertracks"
subscription="82cacb81-4d03-4b46-bf80-141da676ad48"
loc="westeurope"
rgname="rg-"$appname
saname="sa"$appname

dbservername="sql-"$appname
dbname="sqldb-"$appname
dbadminname=$appname"admin"
dbadminpasswd="iKgfh&f823^fnvkwJGs02"

whitelist_name="bart"
whitelist_address="213.127.36.5"

echo Setting subscription: $subscription
az account set -s $subscription

echo Creating resource group: $rgname
az group create --name $rgname -l $loc

echo Creating storage account: $saname
az storage account create -g $rgname --name $saname --sku Standard_LRS --kind BlobStorage --location westeurope --access-tier Cool --https-only

echo Creating database server: $dbservername
az sql server create -l $loc -g $rgname -n $dbservername -u $dbadminname -p $dbadminpasswd
az sql server update -n $dbservername -g $rgname --set minimalTlsVersion="1.2"
az sql server firewall-rule create --r $rgname --server $dbservername --name $whitelist_name --start-ip-address $whitelist_address --end-ip-address $whitelist_address

echo Creating database: $dbname
# Not sure if S1 is strong enough for the purposes we foresee. 
az sql db create -n $dbname -g $rgname -s $dbservername --service-objective S1 
