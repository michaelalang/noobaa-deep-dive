# Multicloud Gateway (MCG) NooBaa Deep dive

The MCG component of Red Hat Open Data Foundation (RHODF) is also commonly referred to as
NooBaa. There are several utilities that can be used to interact with the buckets provided by MCG. The
following tools will be reviewed and demoed:
```
Add buckets from different providers to the
namespace, and access your data in one place to
see a correlation of all your object buckets. Setting
your preferred storage provider for writing enables
seamless migration from and to multiple other
storage providers.
```

Please find the presentation at [MultiCloud_Gateway-NooBaa-Deepdive.pdf](MultiCloud_Gateway-NooBaa-Deepdive.pdf)


# Hand's on plays 

## Bootstrap your NooBaa System

* prerequisits
  - Host/VM with
    - 2 cores
    - 8GB RAM
    - 20 GB Root disk
    - 3x 25 GB (or equal size) Data disks (if you want NooBaa internal storage)
    - Network IP address
    - Software installed:
      - podman
      - ansible
      - python3
        - boto3
    - Internet access
    - quay.io credentials and podman configured on the Host/VM that is target for the NooBaa System

### configure ansible 

create a directory for the plays and configure ansible for that directory
(ensure to name **node2.example.com** accordingly to what your Host/VM is configured for)

~~~
$ mkdir noobaa-deep-dive
$ cd noobaa-deep-dive
$ cat <<EOF> ansible.cfg
[defaults]
inventory      = ./inventory
sudo_user      = root
ask_sudo_pass = True
[inventory]
[privilege_escalation]
[paramiko_connection]
[ssh_connection]
[persistent_connection]
[accelerate]
[selinux]
[colors]
[diff]
EOF

$ cat <<EOF> inventory
NooBaa:
  hosts:
    node2.example.com:
EOF
~~~

ensure ansible is working by ping'ing the node

~~~
$ ansible -m ping NooBaa
node2.example.com | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/libexec/platform-python"
    },
    "changed": false,
    "ping": "pong"
}
~~~

### configure NooBaa playbook variables

at the top of the playbook **play-noobaa.yml** you will find a bunch of variables you can tweak. 
The important ones to modify are:
- ADMIN_MAIL
- ADMIN_PASSWORD
- LOCAL_POOL
  - AGENT_SIZE
  - AGENT_DEVICES

**SYSTEM_NAME** is used to prefix various items (containers, storage,...) you can change it but don't have to.

Depending on if you want to have local NooBaa storage you need to set 
- LOCAL_POOL: true 

and depending on the the required data disk sizes you need to set the size 
- AGENT_SIZE: 25

as well as the correct names for the devices mapped as data disks
- AGENT_DEVICES:
  - { name: "agent01", device: "/dev/sdb" }
  - { name: "agent02", device: "/dev/vdc" }
  - { name: "agent03", device: "/dev/hdd" }

if you do have firewalld enabled on the Host/VM ensure to set 
- FIREWALL: true

### execute NooBaa playbook 

after adapting the necessary Variables in the playbookt, you can run it to deploy your NooBaa system

~~~
$ ansible-play play-noobaa.yml 
PLAY [NooBaa installation] *****************************************************************************************************************************************************************************************

TASK [Gathering Facts] *********************************************************************************************************************************************************************************************
ok: [node2.example.com]

[... output omitted ...]

TASK [create NooBaa Agents] ****************************************************************************************************************************************************************************************
changed: [node2.example.com] => (item={'name': 'agent01', 'device': '/dev/sdb'})
changed: [node2.example.com] => (item={'name': 'agent02', 'device': '/dev/sdc'})
changed: [node2.example.com] => (item={'name': 'agent03', 'device': '/dev/sdd'})

PLAY RECAP *********************************************************************************************************************************************************************************************************
node2.example.com          : ok=32   changed=15   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
~~~

after completing the playbook run successfully you are able to login to your NooBaa Frontend with the credentials adjusted in the playbook at
[http://node2.example.com:8080](http://node2.example.com)

### Administrative configuration tasks

the intention of these tasks is, to get familiar with the NooBaa frontend. The tasks clearly focus on Administrative action items.
There is a *default* Bucket called **first.bucket**. This bucket is not utilized by these exercises and can be deleted if you prefer.

#### configure cloud resources

Outcome of this exercise:
- 2 configured storage resources 
- 2 configured namespace resources

after finishing these tasks your Dashboard should show
- 3 resources
  - 1 pool
  - 2 other S3
- all resources Healthy

##### create new connections 

- click on the left menu bar *Resources* item 
- click on the right hand side *Add Cloud Resource* button
- click on *Choose connection* 
  - click on *Add new connection* 
    - Connection Name: *Minio 1*
    - Service: *S3 V4 Compatible service* 
    - Endpoint: *http://node2.example.com:19000*
    - Access Key: *test*
    - Secret Key: *testS3user*
    - click on *Save*
- click on *Choose connection*
  - click on *Add new connection*
    - Connection Name: *Minio 2*
    - Service: *S3 V4 Compatible service*
    - Endpoint: *http://node2.example.com:29000*
    - Access Key: *test*
    - Secret Key: *testS3user*
    - click on *Save*
- click on *Choose connection*
  - click on *Minio 1*
  - click on *Choose Bucket*
  - select *bucket01*
  - change Resource Name: *minio1-bucket01*
  - click on *Create*
- click on *Choose connection*
  - click on *Minio 2*
  - click on *Choose Bucket*
  - select *bucket02*
  - change Resource Name: *minio2-bucket01*
  - click on *Create*

- click on the left menu bar *Resources* item
- select the tab *Namespace Resources* above the already listed resources
  - click on the right hand side *Add Cloud Resource* button
    - click on *Choose connection*
      - click on *Minio 1*
      - click on *Choose Bucket*
      - select *nsbucket01*
      - change Resource Name: *minio1-nsbucket01*
      - click on *Create*
    - click on *Choose connection*
      - click on *Minio 2*
      - click on *Choose Bucket*
      - select *bucket02*
      - change Resource Name: *minio2-bucket01*
      - click on *Create*

##### create buckets

- click on the left menu bar *Buckets* item
- click on the right hand side *Create Bucket* button
- set *Bucket Name* to *bucket01*
- select Policy Type *Mirror*
- select Resources
  - *minio1-bucket01*
  - *minio2-bucket01*
  - click on *Create*

##### create namespace buckets
- click on the left menu bar *Buckets* item
- select the tab *Namespace Resources* above the already listed resources
  - click on the right hand side *Create iNamespace Bucket* button
    - set *Bucket Name* to *nsbucket01*
    - select Read Policy resources
      - *minio1-nsbucket01*
      - *minio2-nsbucket02*
    - select Write Policy Namespace Resource
      - *minio1-nsbucket01*
    - click on *Next*
    - **do not** enable caching right now for the tests
    - click on *Create*

### scripts to play around with

* prerequisits
  - running NooBaa System
  - 2 running MinIO instances
  - Administrative configuration tasks accomplished

the directory scripts, contains several snippets for showcasing the behavior and API calls.
Additional the minio client binary (mc/mcli) has been downloaded, installed into /usr/bin and configured for the deployed NooBaa and minio instances.

## Access buckets 

### list access 

~~~
$ mcli ls noobaa/bucket01
~~~

### add content 

~~~
$ mcli cp /etc/redhat-release noobaa/bucket01
~~~

### verify content 

~~~
$ mcli cat noobaa/bucket01/redhat-release
~~~

### what happens if one distribution fails

~~~
$ systemctl stop container-minio2 
~~~

### list access still possible

~~~
$ mcli ls noobaa/bucket01
~~~

### content not accessable

~~~
$ mcli cat noobaa/bucket01/redhat-release
~~~

### is this a lasting issue, so restore the availability

~~~
$ systemctl start container-minio2
~~~

### now, verify if the content works again

~~~
$ mcli cat noobaa/bucket01/redhat-release
~~~

## Access Namespace buckets

### empty namespace, normally not what one will encounter

~~~
$ mcli ls noobaa/nsbucket01
~~~

### populate both buckets that are configured for the namespace

~~~
$ echo "blabla" | mcli pipe minio1/nsbucket01/fileA
$ echo "blublu" | mcli pipe minio2/nsbucket01/fileB
~~~

### verify what ends up as namespace

~~~
$ mcli ls noobaa/nsbucket01
~~~

## read/write mirrored Buckets 

- create a mirrored bucket 
  - name the bucket **bucket02**
  - assign two cloud buckets to it
    - *minio1-bucket02*
    - *minio2-bucket02*

### write mirrored buckets 

~~~
$ for r in $(seq 1 10) ; do echo "${r}" | mcli pipe noobaa/bucket02/file${r} ; done
~~~

check in the NooBaa Frontend some random choosen files and their mirror state.

=== cleanup for maintenance and repeat as follows

~~~
$ mcli rm -r --force noobaa/bucket02
~~~

- change the mirrored bucket
  - add the local capacity named **pool0** in addition to the two cloud resources
  - assignment should be
    - *pool0*
    - *minio1-bucket02*
    - *minio2-bucket02*
  - above the Tier 1 resources listed, select *Bucket Policies*
  - select *Edit Data Resiliency*
    - read and understand the Hint on top
    - click on *Advanced Settings*
      - change *Number of Replicas* to two
      - click on *Done*
- repeat the *write mirrored buckets* exercise and see the difference in object mirror states   

Check the Hint ontop why there's only one copy if you configured Cloud resources only.

### disable one side of the mirror

#### first prepare more resources than two to the bucket

~~~
$ for r in $(seq 1 100) ; do echo "${r}" | mcli pipe noobaa/bucket02/file${r} ; done
~~~

#### switch resources and verify errors from the client

~~~
$ mcli ls noobaa/bucket02 | wc -l
~~~

#### hard fail one side of the mirror

~~~
$ systemctl stop container-minio1
~~~

#### create content

~~~
$ for r in $(seq 1 10) ; do echo "${r}" | mcli pipe noobaa/bucket02/file${r} ; done 
~~~

#### verify content during one mirror down

~~~
$ mcli ls noobaa/bucket02/
~~~

#### show noobaa mirror state and restart hard failed mirror

~~~
$ systemctl start container-minio1
~~~

### read/write Namespace Buckets during maintenance

#### disable one part of NS Bucket (writing instance)

~~~
$ for r in $(seq 1 50) ; do echo "file${r}" ; echo "${r}" | mcli pipe noobaa/nsbucket01/file${r} ; done 
~~~

~~~
$ systemctl stop container-minio1
~~~

#### verify that with the first error writing has been stopped

~~~
$ mcli ls noobaa/nsbucket01/
$ mcli ls minio1/nsbucket01/
$ mcli ls minio2/nsbucket02/
~~~

#### hard fail none writing part of NS bucket

~~~
$ for r in $(seq 1 50) ; do echo "file${r}" ; echo "${r}" | mcli pipe noobaa/nsbucket01/file${r} ; done 
~~~

~~~
$ systemctl stop container-minio2
~~~

#### verify that content writing continued

~~~
$ mcli ls noobaa/nsbucket01/ | wc -l
~~~

#### migrate transparently writing instance for the NS bucket

##### first verify the writing instance (minio1-nsbucket01) and nsbucket targets

~~~
$ scripts/show-writing-instance.py 
$ mcli ls minio1/nsbucket01
$ mcli ls minio2/nsbucket01
~~~

##### create content 

~~~
$ for r in $(seq 1 50) ; do echo "file${r}" ; echo "${r}" | mcli pipe noobaa/nsbucket01/file${r} ; done
$ scripts/change-writing-instance.py
~~~

##### verify seemless migration and target change

~~~
$ mcli ls noobaa/nsbucket01 | wc -l
~~~
