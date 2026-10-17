---
title: building a list programming language
date: sept. 30, 2026
---

# what?

\[1\] if i were to write in a dream programming language and then build it, what would it be? it would be a lisp (list programming language) because the syntax is easy enough to grasp and write enough so i can make rooms for other features. it also helps me use ideas in linguistics that i already know (like grammar and shi). but if i were to write in it for the rest of my life, how big would it need to be?

\[2\] for starters, c is not that big. it's low-level but you can learn it in like 2 weeks. that's why i don't want to switch to c++ and that's why i stuck to python for so many years. i really like a page of "introduction to zig" that says this well:

> This philosophy becomes clear with the following phrase from the official website of Zig:
>> “Focus on debugging your application rather than debugging your programming language knowledge”.
>This phrase is specially true for C++ programmers. Because C++ is a gigantic language, with tons of features, and also, there are lots of different “flavors of C++”. These elements are what makes C++ so complex and hard to learn. Zig tries to go in the opposite direction. Zig is a very simple language, more closely related to other simple languages such as C and Go.
>
>The phrase above is still important for C programmers too. Because, even C being a simple language, it’s still hard sometimes to read and understand C code. For example, pre-processor macros in C are a frequent source of confusion. Sometimes, they really make it hard to debug C programs. Because macros are essentially a second language embedded in C that obscures your C code. With macros, you are no longer 100% sure about which pieces of the code are being sent to the compiler, i.e. they obscure the actual source code that you wrote.
>
>You don’t have macros in Zig. In Zig, the code you write, is the actual code that gets compiled by the compiler. You also don’t have a hidden control flow happening behind the scenes. And, you also don’t have functions or operators from the standard library that make hidden memory allocations behind your back.
>
>By being a simpler language, Zig becomes much more clear and easier to read/write, but at the same time, it also achieves a much more robust state, with more consistent behaviour in edge situations. Once again, less is more.

\[3\] by the way, i'm naming this "arsp" for the time being because it sounds cool. basically the goal is not to make this more math-y because 1) you can already make math-y things in lisp and 2) there's lean and coq so originality out the window. i'm intending to make arsp a functional language where i said "can replace other languages" (for me, i don't encourage religion or strong preference)

# what's how (compiler design)

\[4\] we're not going to talk about the features yet because i'll leave that up to making sample code for arsp so i can work out from there. but to build a compiler for arsp, we're going to need:
* lexer → splits source code into tokens
* parser → converts tokens into ast
* codegen → generate c code<sup>(1)</sup>
* runtime environment → resolve variables, functions, and scopes

# what's what (syntax design)

\[5\] of course, being a lisp, it'd be the obvious choice to keep like 80% of what's already in lisp (i'll use common lisp docs as reference). all lisp really contains are s-expressions which are atoms (they are irreducible and evaluate to themselves) or lists (which contains atoms)

## TBC (please wait, this post is unfinished)