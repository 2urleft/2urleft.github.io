---
title: post name
date: sept. 6, 2026
---

the post title should be "post name", don't worry about it.

---

## notable writing conventions

\[1\] each paragraph is written with a paragraph marker before it. not only is it easier to reference to a previous paragraph but the visual separation of the marker being there (similar to Cambridge's Global English textbooks) helps to read better.

\[2\] there are no ui primitives like containers that store text like a special hint or "did you know" or "tip" box. although it's limiting, a blog written like this encourages me to write more readable text when it's sequential like paragraphs and essays.

\[3\] each header shouldn't be too short. a header 1 is permitted to have 2 words at least but any smaller header should be written with the main idea clearly. there's no particular reason for this other than i saw it inside a research report on my literature textbook and it's really helpful.

## things to consider implementing

\[4\] is it worth it to have diagrams? that would violate my ui primitive idea unless it's an image. but still, talking about having diagrams kind of ruin everything so far. however, it'd be much easier to accept if it looked comparable to this:

![](/assets/layout.png)

you can see that there is no in-depth detail and the background is transparent. excalidraw (which is what i used to make the diagram above) is an extremely good tool at doing this. if diagrams are helpful, the answer would be "yes, diagrams are worth it".

\[5\] footnotes are essential and i also wanted to add it into [notable writing conventions](#notable-writing-conventions) but it's going to be tricky since i don't think we can nor need to automate creating footnotes. instead, what i planned was that you would write a footnote in superscript like this<sup>(1)</sup> enclosed by parentheses.

---

\(1\) and placed whereever the writer wants as long as it is marked with a footnote marker also enclosed in parentheses. it also introduces some harmony and distinction with paragraphs and their markers as well. it's advised to place the footnote at the end with a separator though to be separated by layout clearly.

---

\[6\] the implementation of latex is <s>underway</s> done since it's incredibly essential to a tech blog. here's what it looks like right now:

$$e^{i \pi} = -1$$

very original i know, but still a decent demonstration as of the time of writing.

\[7\] lastly, i want to be able to express time-gaps without writing "as of writing this in __", it's underway right now and i plan for it to go as a tiny font text saying the date and time aligned to the right (and cutting a dotted separator if possible). this post is in no need for a time-gap so demonstration will be up to any future post.