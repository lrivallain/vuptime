---
layout: post
title: REST ❤ Swagger, 2 minutes to create an API SDK ⏱ – Codegen Demo – Part 1
author: lrivallain
category: Automation
tags: rest swagger devops codegen api vcenter vcloud vmware
thumb: /images/rest-loves-swagger/APIEverywhereMeme.png
---

On March 30<sup>th</sup>, I presented a webinar to the French VMUG community on the REST API subject and in particular on the way to generate API SDK clients without writing any code.

Slide deck is published (only in french, sorry) here: [https://vupti.me/rls](vupti.me/rls).

As said in the slide deck, this presentation was greatly inspired by a VMworld session: [{CODE2216E} The art of code that writes code](https://videos.vmworld.com/global/2019?q=The%2520Art%2520of%2520Code%2520That%2520Writes%2520Code) (Kyle Ruddy @ VMware Inc.). I cannot encourage you enough to see the replay if you did not do it yet.

The only part I did not pulished yet, was the demo part (even if, curious people may have found it [in the repository](https://github.com/lrivallain/rest-loves-swagger/blob/master/demo/Swagger%20Code%20Gen%20%5BDemo%5D.ipynb)).

I was planning to find a way to host the Jupyter Notebook online but as some commands rely on docker commands... I could not fount a hoster that enable it. So, let's re-write it in 2 blog posts.

* Table of contents
{:toc}

## Target of this post

So this post aims to demonstrate how you can create API SDK clients with [Swagger Codegen](https://swagger.io/tools/swagger-codegen/):

* Based on API documentation (both OpenAPI OASv3 and Swagger v2 are supported)
* In the language of your choice (see below for the list)
* Whitout writing any single line of code yourself (except for **usage** of the generated SDK)
* In minutes !

Impossible? Let's see.

### Next post

In a second post, I will demonstrate how to build/use SDK for VMware products: vCenter and vCloud Director.

## Prerequisites

### Docker

First, we need a docker setup (in order to avoid installing locally, the codegen software). I won't explain how to install and configure a docker host, this is not the point of the post.

We get the docker image of Swagger Codegen:

```bash
docker pull swaggerapi/swagger-codegen-cli
```

If you prefer a local installation of Codegen, [it is possible](https://github.com/swagger-api/swagger-codegen#compatibility) but you will need to modify some of the following commands.

### Folders structure

For the tests, we will create 2 folders, for `in`put files and `out`put ones within a `codegen` folder:

```bash
mkdir -p codegen/in/ codegen/out/
ls codegen/ # should output "in out"
```

### Python

We will create some python modules for test. I suggest to use a virtualenv if you want to proceed the same tests and to install some dependencies:

```bash
wget https://github.com/lrivallain/rest-loves-swagger/raw/master/demo/requirements.txt
wget https://github.com/lrivallain/rest-loves-swagger/raw/master/demo/utils.py
pip install -r requirements.txt
```

> **Warning:** I strongly suggest that you review the content of all the files you download on your computer before using them!

### Go

A part of this post will provide a Go module. Install Go runtime to be able to test it.

## Available languages

Codegen supports tons of output languages. To demonstrate it, we can use the following command:

(The `sed` part is only to prettify the ouput)

```
docker run --rm swaggerapi/swagger-codegen-cli langs | sed 's/,/\n    /g'
```

The output of the command will be something like:

```
Available languages: [ada
     ada-server
     akka-scala
     android
     apache2
     apex
     aspnetcore
     bash
     csharp
     clojure
     cwiki
     cpprest
     csharp-dotnet2
     dart
     dart-jaguar
     elixir
     elm
     eiffel
     erlang-client
     erlang-server
     finch
     flash
     python-flask
     go
     go-server
     groovy
     haskell-http-client
     haskell
     jmeter
     jaxrs-cxf-client
     jaxrs-cxf
     java
     inflector
     jaxrs-cxf-cdi
     jaxrs-spec
     jaxrs
     msf4j
     java-pkmst
     java-play-framework
     jaxrs-resteasy-eap
     jaxrs-resteasy
     javascript
     javascript-closure-angular
     java-vertx
     kotlin
     lua
     lumen
     nancyfx
     nodejs-server
     objc
     perl
     php
     powershell
     pistache-server
     python
     qt5cpp
     r
     rails5
     restbed
     ruby
     rust
     rust-server
     scala
     scala-gatling
     scala-lagom-server
     scalatra
     scalaz
     php-silex
     sinatra
     slim
     spring
     dynamic-html
     html2
     html
     swagger
     swagger-yaml
     swift5
     swift4
     swift3
     swift
     php-symfony
     tizen
     typescript-aurelia
     typescript-angular
     typescript-inversify
     typescript-angularjs
     typescript-fetch
     typescript-jquery
     typescript-node
     undertow
     ze-ph
     kotlin-server]
```

Pick the one you need !

## Chuck Norris

We will use a sample API ([api.chucknorris.io](https://api.chucknorris.io)) for a first test.

Here is our plan:

1. Get API documentation (from [api.chucknorris.io/documentation](https://api.chucknorris.io/documentation))
1. Pretify with `| python -m json.tool`
1. Store the result in a file
1. Display the first lines

```bash
curl -s https://api.chucknorris.io/documentation | python -m json.tool > codegen/in/chucknorris.json
head -n 25 codegen/in/chucknorris.json
```

You should see the content of a swagger file, with the API description.

### Package configuration

We will create a Codegen configuration file for a python module, with some information about naming and versioning.

```bash
echo '{
  "packageName":"chucknorris_client",
  "projectName":"chucknorris-client",
  "packageVersion":"1.0.0"
}' > codegen/in/config_chucknorris_client.json
```

### SDK generation

Now we specify to Codegen, to use both API documentation file and package configuration one to create a new **`python`** based client SDK:

```bash
docker run --rm -v ${PWD}/codegen:/local \
  swaggerapi/swagger-codegen-cli generate \
    -i /local/in/chucknorris.json \
    -o /local/out/python-chucknorris \
    -c /local/in/config_chucknorris_client.json \
    -l python
```

We now have a new python module:

```bash
ls codegen/out/python-chucknorris/
```

Output:
```
README.md	    git_push.sh       test
chucknorris_client  requirements.txt  test-requirements.txt
docs		    setup.py	      tox.ini
```

And we can pip install this module:

```bash
pip install codegen/out/python-chucknorris/
```

### Use our new module

We create and run the following python file to use our new module:

```python
import chucknorris_client
from chucknorris_client.rest import ApiException

from utils import *
logger = logging.getLogger("DEMO_CHUCKNORRIS")

# Configure API
logger.debug("Create an API client")
client = chucknorris_client.ApiClient(chucknorris_client.Configuration())

logger.debug("Target the Joke Controller")
api_instance = chucknorris_client.JokeControllerApi(client)

try:
    logger.debug("Get a random joke:")
    api_response = api_instance.get_random_joke_value_using_get()
    logger.info(api_response)
except ApiException as e:
    logger.error(
        "Exception when calling JokeControllerApi->get_random_joke_value_using_get: %s\n" % e
    )
```

You can now run it and get the following result:

```
DEMO_CHUCKNORRIS 	Create an API client
DEMO_CHUCKNORRIS 	Target the Joke Controller
DEMO_CHUCKNORRIS 	Get a random joke:
DEMO_CHUCKNORRIS 	Chuck Norris was worshipped as a god by the Eskimos. That is why they had igloos modelled after his signature move.
```

Please consider that most of the python code we used is about the logger and not the complexity of getting a random Chuck Norris fact. If you don't, Chuck Norris may come to you for an explaination.

### Same with Go ?

Lets do the same, with Go:

```bash
docker run --rm -v ${PWD}/codegen:/local \
  swaggerapi/swagger-codegen-cli generate \
    -i /local/in/chucknorris.json \
    -o /local/out/gochucknorris \
    -DpackageName=gochucknorris \
    -l go
```

The `Go` test file (for example: `codegen/chuck.go`):

```go
package main

import (
    "log"
    cn "out/gochucknorris"
    "golang.org/x/net/context"
)

func main() {
    log.Print("New API client with empty configuration")
    client := cn.NewAPIClient(cn.NewConfiguration())
    log.Print("Get random joke")
    joke, r, err := client.JokeControllerApi.GetRandomJokeValueUsingGET(context.Background(), nil)
    // Test error
    if err != nil {
        log.Print("Error:", err)
    }
    // Test HTTP Response code
    if r.StatusCode == 200 {
        log.Print(joke.Value)
    }
}
```

And the result of a `go run codegen/chuck.go`:

```
2020/04/01 17:28:11 New API client with empty configuration
2020/04/01 17:28:11 Get random joke
2020/04/01 17:28:12 Chuck Norris can levitate birds.
```

## Conclusion

How long to get this new API SDK client in a new language? Less than a minute !

In the next post, we will apply this process to two VMware products:

* vCenter (6.7 only sorry!)
* vCloud Director