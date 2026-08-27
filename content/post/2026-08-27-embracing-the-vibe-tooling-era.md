---
title: "Embracing the vibe tooling era"
date: "2026-08-27"
author: lrivallain
author_name: Ludovic Rivallain
description: "Why the answer to fourteen personal tools isn't a fifteenth."
categories:
- Thoughts
tags:
- AI
- Tools
- Vibe coding
- Organization
- Productivity
thumbnail: /images/vibe-tooling/thumbnail.png
featureImage: /images/vibe-tooling/hero.png
toc: true
---

**For once, this post won't be technical — it's more of a step-back piece.** In the AI era, a lot of things have accelerated dramatically and, from where I stand in particular, I'm seeing a new trend I wanted to share a few thoughts about. I've called that trend "vibe tooling". What follows applies mostly to the IT and cloud world I work in, but I wouldn't be surprised to see the trend spill over into other fields little by little.

## Vibe tooling?

Where vibe coding is about building software with AI assistance, what sets vibe tooling apart, to me, is the intent to solve a more specific problem — recurring or not. Either way, what comes out is AI-generated code. But in the second case, you're not trying to build a product or a deliverable: what you're translating into code is your own way of working.

*The tool you needed that morning, for yourself, for the task in front of you.*

A recent example, about as mundane as they come. An escalation to handle on a batch of backlog requests: a lot of people to contact, each with a message tailored to their own request, and yet a strictly identical set of instructions from one message to the next. One hour to build the tool. A day saved, probably more. And by that same evening it had no reason to exist any more: the matter was closed.

Except it got used again. Today it serves me, occasionally, to run small communication campaigns about backlog items. Nobody decided it should survive, least of all me: usage decided, after the fact.

"Before" the generative AI era, the maths were simple and usually came out negative — the time spent building the tool against the time it would save. Today the tool gets built in an hour, in the background, and a whole set of small frictions we used to just put up with become tractable. The ratchet effect, which I'll come back to later in this post: experience feeds the improvement of whatever comes next in an activity, through its ability to be converted into tooling.

Vibe coding produces software. Vibe tooling produces ways of working. Some of these tools don't survive the week, others settle in for good — and that's the point where the subject invariably travels up from the individual to the organization they belong to.

## Tools in history

I'm not going to cover the history of tooling at length here, not even within IT alone… there would be far too much ground, in forms so varied and so rich that they are now simply part of our daily lives.

Without this ability to design and pass on tools, our species would probably have followed a very different trajectory — one of limited intergenerational transmission, where each generation relearns what the previous one had already figured out. The "ratchet effect" (Tomasello — *The Cultural Origins of Human Cognition*, 1999), specific to our cumulative cultural evolution, rests in particular on this ability to externalize what we have learned into objects, methods, representations.

By its very nature, the IT world is also heavily dependent on the notion of tooling: the ratchet effect is particularly amplified there by machines' capacity for computation, automation and autonomous work.

## Tools in *my* history

One of the great sources of interest I've found in IT, engineering and cloud systems architecture over the course of my career has been the ability to automate tasks.

In 2006, I was lucky enough to be introduced to the incredible power of making things run predictably, reproducibly and autonomously, right from my first real professional experience. Back then, we were coding test platforms for multi-protocol routers. Every night, a few racks of assorted equipment would verify that other engineers' software development work hadn't broken support for telecommunications protocols. In the morning, we collected the results, shared them with the relevant teams, then worked on improving our test protocols and our platforms. Gilles, who shared my office at the time, was the one who revealed to me that incredible power of putting machines to work, even when I wasn't there.

Now that the professional experiences have piled up, I can see one constant has remained in my work: if a task is going to be long, repetitive, or require some complex assembly, I'm quick to automate it and let a tool do the work rather than doing it by hand. I didn't become a developer — that was never the goal, and it isn't where I add the most value either. But I script, I script a lot. And sometimes those scripts end up looking like small applications, small websites, even services shared with others.

Recently, with the rise of vibe coding, I've been able to work on more ambitious projects such as [Azure Scout](https://docs.az-scout.com/). And while vibe coding changed a few parameters (quality, execution speed, the complexity of scenarios you can attempt, layering AI models on top of more classic features…), it also changed another, more fundamental aspect whose implications took me a while to grasp.

## The bloom

AI coding assistance changed my velocity, but above all it's a concept that gave wings to people who until then had no development experience whatsoever. Those people had needs, ideas, creativity all the same. And often they don't carry the constraints someone from a software development background imposes on themselves. And coding assistants, for a few million tokens, go on to find the path that turns those ideas into reality.

So we're seeing (in my organization at least) a multitude of tools arriving, often coded:

- by the most "technically comfortable" among those who didn't necessarily know how to code;
- by those who do it for a living, or whose skill set already allowed them to build scripts, programs, small websites, and so on.

It's all blooming, and it's getting hard to keep track of who is doing what, why, and within which framework. And since organizations like frameworks, they try to define some for these initiatives.

## On choosing the framework

> "My employees are coding tools off in their corner. What do I do?"

There are inevitably plenty of subtleties to bring to an organization's answer when facing this bloom of new tools.

The first approach might be to ban the phenomenon outright. It's radical, and if that stance worked, it would prevent any drift. Reality is probably more mixed, and "*life finds a way*": deprived of AI tools or of freedom of use, shadow IT comes back in a new form, and the risk grows of seeing employees use tools ill-suited to the sensitivity of the data they submit.

At the opposite end of that radical approach, blanket approval with no guardrails for assorted, unmanaged AI tools and solutions exposes the organization to risks that are every bit as monstrous.

So the right balance has to be found: steer usage towards approved solutions without blocking initiative. For instance, impose a given AI platform, but leave room for individuals to build additional tooling on top.

- If the platform choice was the right one,
- and if data protection and the right access controls are in place,
- and if a user wants to build a tool to make their work easier,
- and if that tool doesn't take data outside the already-approved perimeter,
- then: that need carries no additional risk. We're in the realm of optimization.

## One tool to rule them all

> "… one tool to find them, one tool to bring them all, and in the darkness bind them"

All too often, within organizations, comes the urge to make these initiatives converge into a single framework, a single tool. Gather the good ideas, the good tools, and make just one out of them.

Appealing as the idea may look, it seems to me to suffer from a number of flaws:

- Is the ambition to improve an existing tool with the ideas developed in individual initiatives? If not, why not deal with the matter at the source?
- Is the ambition to back this future "single" tool at the highest level of the organization concerned? If not, this new initiative simply adds itself to the others and will certainly have neither the expected adoption nor the sponsorship/mandate needed for it to evolve over the long term.
- Won't moving from a voluntary initiative — individual, or carried by a small group — to a more substantial project considerably reduce the initial velocity? Where an idea used to become a tool in a few hours, if it now takes discussion in a wider group, sign-off on a change, on a pattern, and so on, there's a serious risk that velocity collapses and that process complexity wins out over the initial inspiration.

And there is, I think, one element too often overlooked: we don't all work the same way. In equivalent roles, in knowledge work, individuals develop their own way of working. The influences and variations are many:

- other colleagues;
- personality;
- education;
- familiarity with one tool or another;
- subtle variations in the assignments handed out;
- personal and professional rhythm;
- experience;
- and so on.

Wanting to offer a single way of working leads to creating a framework that is potentially less efficient and less interesting for some people.

In my experience, many initiatives, in perfectly good faith, propose a way of operating that fits the person or group who designed it more than it fits the whole set of potential users. As long as adoption stays voluntary, that is neither abnormal nor serious, provided a few points are accepted:

- this variety of profiles is probably an asset for the organization;
- a tool may fit a given profile… or not. And that "or not" is certainly the most important part;
- there's no harm in having built a tool that isn't adopted by everyone you initially had in mind.

All of this holds on one condition, however: that the tool remains offered, not prescribed.

## So what should we do?

Vibe coding and vibe tooling initiatives allow some people to work around the weaknesses of the tools already available to them, while applying their own methodology. This serves several goals, specific to each initiative: saving time, handling a subject better, correlating data, finding a more suitable representation, and so on.

And for me, there are two interesting possibilities for an organization facing this bloom of tools:

- feed the backlog of the tools the entity operates, based on this feedback from the field;
- let some initiatives carry on as they are.

The distinction between the two is simple:

- if it belongs to individual practice, to preferences, to a particular way of working: then the tool isn't meant to be imposed. Its adoption must remain natural. The people who adopt it will be compatible with the initiative and will feed it to improve it over time;
- if it belongs to the mandatory operation of the organization: then it has to enter that organization's tool evolution process.

That leaves the most frequent case, and the most interesting one: when three people come and ask for the tool you built for yourself. That's not a problem, it's information — the need wasn't so personal after all. Sharing the tool changes nothing about its status: it remains offered, with no guarantee and no commitment — and it is perfectly legitimate to say so. What does deserve to be escalated, on the other hand, is the need itself, to where it can be handled with the appropriate mandate.

## Neither one nor the other

There remains a third model, which I didn't list among the two possibilities — because it isn't one. And yet it's the one you come across most often.

The mechanism is fairly readable. An individual tool works. It gets shared, first within a small circle, then a little beyond. An intermediate entity then picks it up to turn it into a tool "for everyone" — without it ever having become everyone's tool. It gets a name, sometimes a team, often a roadmap. And it is decreed to be, from now on, the way of working.

The operation has a definite advantage for whoever runs it: it gives the appearance of having addressed the need, without having to carry it to where it should be carried. Carrying a need at organization scale means accepting trade-offs, a review, accountability, a budget, a lifecycle — and the very concrete risk of being told no. By handling it locally, you spare yourself all of that. You don't solve the problem: you work around it, and capitalize on someone else's work along the way.

The grievance isn't the size of the entity carrying the tool. A tool carried by a team, a subsidiary or a division for its own activity is perfectly legitimate, whatever its scale. What isn't legitimate is the gap between the perimeter that sponsors and the perimeter it prescribes to.

And this is where the asymmetry deserves to be named:

- a tool backed at the highest level can impose a way of working: that is exactly what sponsorship buys it. And that right is paid for — accountability, a lifecycle, a budget, an obligation of results, someone who can be held to account;
- an individual tool imposes nothing on anyone. It therefore has no reason to be accountable for anything, and that is precisely what makes its freedom acceptable;
- the intermediate tool, on the other hand, prescribes without being accountable. It has taken the right to impose without taking on the obligations that ground that right.

It is this asymmetry, far more than any consideration of adoption or efficiency, that makes me say these intermediate consolidations are doomed to fail. They ask others to change their way of working, in exchange for a commitment nobody has the mandate to honor.

## What about maintenance?

I already know a few arguments that will be raised against this very personal opinion, starting with the lifecycle of these tools: who maintains them, what becomes of them when their author leaves, how do you handle vulnerabilities in their dependencies, what do you do about silent duplicates and abandoned projects?

I certainly won't be making the case for an unmaintained software layer or for risky dependencies. But I think this risk needs to be looked at from a different perspective.

- If adoption was natural, the tool's community has a better chance of holding at a level sufficient to keep that asset alive — not least with the help of the code assistance tools we have today. And if usage naturally dwindles, the associated risk decreases with it. This is particularly true of scripts and tools that run on localhost, on workstations.
  - This assumption collapses as soon as the tool is hosted, holds credentials, or acts as a gateway for other people.
- If adoption was more forced, it's a safe bet that maintenance will have to be forced too, over a long stretch of time… perhaps too long for certain human or organizational balances. The imposed framework creates its own friction here, and someone has to carry it over time — that is to say, precisely, someone who has the mandate for it.

There is also a risk that gets talked about less, and which strikes me as more serious than breakage. A tool built in an hour produces clean, fluent output that looks authoritative — and its implicit assumptions, what it rounds off, what it ignores, are written down nowhere. As long as the author is its only user, that isn't a problem: they hold those assumptions in their head, and that is precisely why they never needed to write them down. The risk only appears the moment the tool circulates and prescribes without anyone ever having reviewed those assumptions.

## Letting the ratchet turn

Our tools have always served that purpose: turning what we have learned into something we will never have to learn again. What generative AI changed isn't the nature of the mechanism — it's its speed, and the number of people able to operate it.

Faced with this bloom, the convergence reflex fires at every level. It's understandable: proliferation is uncomfortable, hard to map, to secure, to justify. But wanting to bring everything back to a single tool means taking away from the mechanism the very thing that makes it work: the proximity between the person who has the problem and the person who builds the answer. And more often than not, the attempt to unify fourteen tools simply produces a fifteenth — the famous [XKCD 927](https://xkcd.com/927/).

So the right question isn't "how many tools?", but "who has the mandate to impose one?".

Gilles had shown me that machines could be put to work even when we're not there. Twenty years later, they also build the everyday tools. It's up to us not to jam the mechanism.

---

*Header image: ["Standards"](https://xkcd.com/927/) by Randall Munroe (xkcd 927), used under a [Creative Commons Attribution-NonCommercial 2.5 License](https://xkcd.com/license.html).*
