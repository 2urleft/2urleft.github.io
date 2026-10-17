---
date: oct. 13, 2026
title: building an authoring interface for this blog
---

\[0\] recently i made an arg (which i'm not going to show you because it's secret) that enables puzzle authors to communicate with each other and draft puzzles as threads like in slack. it's going to be hard not to brag about it because i brag about everything,

\[1\] deciding that i need to have some type of convenient system to write my blogs instead of hopping on to vscode is probably a good takeaway from that. sidenote: i do have this project (the tool) on my lms portfolio (just discovered my lms has a portfolio feature).

# proof of concept

\[2\] i'm thinking an interface like this would suit me well enough for this project:

![](/assets/toolpoc.png)

1. it has a tree (similar to the archive tree that you see in this blog's `/posts`) that neatly organizes posts by date, this is to prevent it from ever looking like my original workflow:

![](/assets/currentworkflow.png)

although the workaround is to add a prefix behind each post/asset, that's one part of the problem only. vscode even though is a really really good editor (writing markdown in it is even comfortable), it's not built for writing blogs

2. specialized markdown editor (can be an lsp-compatible text editor)
3. inspector panel that can change metadata, kept separate from the editor

\[3\] as for the stack, i'm thinking qt since a while back i made another personal project (made with ai so i didn't include in the blog) called "qtmega" that's like a huge development environment with every window as a qt utility/process and each workspace allows visual organization of utilities for development. although i scrapped qtmega, it'll be great if i revive the project and be able to add this tool in as a utility!

# development

<p class="timegap"><time datetime="2026-10-17">oct. 17, 2026</time></p>

\[4\] development has been going like a breeze! i started with the simple 3 dock layout and added a simple text area. i tried to make the app as less attuned to my blog as possible but i don't think a lot of people write static sites in markdown so i guess it's already kind of far from general. in this version there's an actual explorer dock with chronological tree (but from the file creation date, not from the frontmatter since metadata is not reliable) and a metadata inspection dock that can change frontmatter key-value pairs

\[5\] there's actually another feature called "tools" where you can import custom programs to run when the button is clicked. this is helpful for compiling my posts and potentially forcing conventions onto posts where there's violations or i'm too lazy to follow.

![](/assets/blogwriterdemo.png)

\[6\] i might consider a feature where you might be able to access the folder for your assets and import it easily through blogwriter