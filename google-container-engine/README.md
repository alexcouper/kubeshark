# Google Container Engine

Get started: https://cloud.google.com/container-engine/docs/before-you-begin

Install gcloud and kubectl command line utils (you need python 2.7):
```
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud components update beta
gcloud components update kubectl
```

Set up access.
```
gcloud config set project $PROJECT-ID
gcloud config set container/cluster $CLUSTER-NAME
gcloud config set compute/zone $ZONE
gcloud auth login
gcloud beta container clusters get-credentials
```

You'll need this in future if you ever want to switch between kubernetes
clusters.
```
kubectl config set current-context $CONTEXT
```

Find the context name by looking at the kubernetes config
```
kubectl config view
```

## Pushing images to GCE

Tag the image
```
docker tag user/example-image gcr.io/your-project-id/example-image
```

Push the image to GCE
```
gcloud docker push gcr.io/your-project-id/example-image
```

## Accessing the UI

The web UI is running on the master.
```
$ kubectl cluster-info
Kubernetes master is running at https://XX.XX.XX.XX
KubeDNS is running at https://XX.XX.XX.XX/api/v1/proxy/namespaces/kube-system/services/kube-dns
KubeUI is running at https://XX.XX.XX.XX/api/v1/proxy/namespaces/kube-system/services/kube-ui
Heapster is running at https://XX.XX.XX.XX/api/v1/proxy/namespaces/kube-system/services/monitoring-heapster
```

However, going to the KubeUI directly will prompt you for authentication details.

Instead, have kubectl run a proxy and it will handle authentication correctly:

```
$ kubectl proxy --port=8001
```
Now go to http://localhost:8001/api/v1/proxy/namespaces/kube-system/services/kube-ui

## Architecture

A single postgres db container.
A load-balanced set of api-only app containers.

## Debugging live

To get a pod name:

```
$ kubectl get pods
```

To run execute commands against a running pod:
```
kubectl exec -ti <pod_name> bash
```

To see the log output (ie stuff written to stdout/stderr - which is where apache
is logging to)
```
$ kubectl logs <pod_name>
```

## Upgrading the set of pods in a controller.

Assuming that:
 - you've already pushed a new tagged image to the google container registry
 - you just want to perform an upgrade of the image deployed:

 ```
 $ kubectl rolling-update <RC-name> --image=<path-to-image>
 ```

 There are plenty of other things you may want to upgrade using rolling-update.
 For more information, look at:

 ```
 $ kubectl rolling-update --help
 ```

# Getting things going.

This section is here to provide a reference for how we got things set up on
kubernetes with GCE.

## Creating persistent storage for use by the database.

Largely found [here](https://cloud.google.com/container-engine/docs/tutorials/persistent-disk/).
Slight issues I had:
 - Mounting location (had to alter PGDATA to be a sub directory of the mount point)
 - Debugging - two containers can't reliably share the mounted drive, or at least
   I had issues.

## Setting up the database.

I created the pod:
```
kubectl create -f google-container-engine/postgres.json
```

However, this pod was always in PENDING/WAITING status.
```kubectl describe postgres```
helped to diagnose this (and later ```kubectl logs postgres```).

Initial issue was that we didn't have enough resource space due to the limits
specified on the postgres pod. I extended the cluster by creating another node
using the gcloud api:

```
gcloud compute instance-groups managed resize <cluster_group>
--zone <zone> --size 2
```

Then, after recreating the nodes, all seemed to work.

I made sure that the db we wanted existed:
```
kubectl exec -ti postgres bash
su postgres
psql
> CREATE DATABASE kubeshark
```
And matched that up with the env vars in the api-rc.json file.

## Getting the db to be discoverable

I created a postgres service so that our app containers can find the db through
DNS (discovery!).
```
kubectl create -f google-container-engine/pg-service.json
```

## Recreating the nodes we needed.

In order to get the DATABASE_URL env var present, I recreated the RC and its
containers.

```
kubectl stop <replication controller>
kubectl create -f google-container-engine/api-rc.json
```

I then bashed my way in:
```
kubectl exec -ti <container> bash
```
and ran syncdb FTW!

You can now login to kubeshark admin at http://XX.XX.XX.XX/admin/

To find this address, use ```kubectl get service```.
