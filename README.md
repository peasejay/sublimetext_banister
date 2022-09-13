# SublimeText Banister plugin

## The General Problem

In my adventures, I somehow often find myself in situations where I want to add markup to a text file but, without actually CHANGING the text file. As we all know, markup, like HTML or whatever, is cool because it adds a metadata overlay to a text file that can than be "hooked" into using a web browser or CSS presentation or some such post-processer to add either formatting or functionality.

This is all wonderful, but as a file becomes marked up, one loses one's ability to actually edit the CONTENT of text file - it can be hard to gauge how a paragraph actually "reads" when there is a bunch of markup in the way.

This SublimeText plugin approaches the problem by allowing passages of a text file to be highlighted and tagged in SublimeText, and then that metadata saved to a separate "sidecar" file, either for reopening back into SublimeText (to allow further revisions) or for later processing using a separate script.

I am going to proceed to discuss the specific problem I'm trying to solve with this plugin, but want to first emphasize that this approcah can probably be useful in other text file editing domains as well. For instance, a similar plugin could be made to apply more general HTML markup to a text document.


## The Specific Problem

As I mentioned, the above is a general workflow problem I have encountered with editing text files. However, the specific use case that actually prompted me to build this plugin is fairly ridiculous and likely won't be that useful to you. Sorry in advance.

This specific script is meant to be used to replicate the formatting that I found in Manly Banister's 1950 Science Fiction fanzine [Nekromantikon](https://fanac.org/fanzines/Nekromantikon/) (shortened colloquially to Nek in this document). Basically, Nek was a magazine that was printed out in one guy's garage using a variety of old-timey printing technologies (mimeograph, lino-printing, photoengraving on zinc plates) in 1950 and 1951. There are a lot of things about Nek that are interesting to me, but one that I kept thinking about when I first saw it was that it had a fully justified layout that was *fully executed on a typewriter*. I became more intrigued when I noticed that some of the spacing in Banister's lines were not evenly monospaced like you'd see on a normal typewriter - Banister was actually using combinations of spaces and half spaces to pad his characters.

![Nekromantikon's fully justified blocks of text](img/nekromantikon.png)

Now, the most common response that people have when I bring this up is usually along the lines of "...yeah, so?". But due to my own personal limitations, I started to become very interested in how Banister would have executed this. 

This all seems like an absurdly complicated process to undertake manually. Nekromantikon had a page count of 50-90 pages over its run.

Here is the algorithm that would have been required to make this happen.

    1. Count the characters on each line. Most lines in Nekromantikon 2 are exactly 66 characters long.

    2. Where a line is a few characters longer than 66 characters, substitute some of the double spaces in the line with normal spaces OR some of the spaces with half-spaces.

    3. Where a line is a few characters shorter than 66 characters, either substitute

Note that Banister's padding changes involving half spaces always need to be balanced - half spaces need to be added to a line in multiples of 2. Banister accomplishes this by always applying padding changes both before and after a word OR by adding half spaces in between the letters of a word with an odd number of characters.


![Banister-highlighted text in SublimeText editor](img/nekromantikon_edits.png)


## Commands

Commands can generally be run either from the 'Banister' Menu on the applications menu bar or from the context menu available from right clicking in the editor window.

### Add/Remove Short Border

Flags the current selection as being surrounded by half spaces.

### Add/Remove Stretch Border

Flags the current selection as being surrounded by 1.5-width spaces.

### Explode/Unexplode Word

Flags the current selection as containing half spaces between each character of the word. Should only be used on words with an odd number of characters to retain a blanced number of characters.

### Add/Remove Underline Region

Flags the current selection as being underlined.

### Reset Regions for Selected

Removes all Banister regions that contain the current character position (useful for undoing formatting mistakenly applied multiple formats).

### Import MBN Regions

Manually load an MBN sidecar file for current file and apply overlay to current document. This is normally run automatically when a text file that has an available sidecar file is loader into SublimeText.

### Export MBN Regions

Manually save an MBN sidecar file for current file and apply overlay to current document. This is normally run automtaically when a text file that has an available sidecar file is saved from SublimeText.

### Count Justified Line Lengths (Application menu only)

Runs through each line of text file in SublimeText and displays the character count of each line with formatting overlay applied. Lines of the correct length are decorated with green highlights, lines that are long are decorated with red highlights, and lines that are short are decorated with orange highlights.

Note that short lines will be fairly common in practice because the last line of paragraphs as well as paragraphs that cover only a single line are not justified. Long lines are more rare in Banister's output (as they imply that somebody made a mistake in applying the algorithm), but in some cases he does exceed his planned line character count (note the line starting "phone somebody in Lefarge..." (line 808 in the SublimeText screenshot) for an example of this) in the actual Nek.

### Render HTML Output (Application menu only)

Exports an HTML version of the current document with fully rendered document markup applied. This is the "final" output of the Banister markup process.