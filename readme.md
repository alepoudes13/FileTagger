# Files Tagger
Allows to mark files with your own tags and then search by tags or filename.<br>
Previews are available for images and videos.<br>
### Tagging
To tag files select them or their tags on the list and press Enter. Tags are added one at a time. Press Enter to submit a tag, Tab to use the first suggested, KeyDown to scroll the suggestions list. Escape to finish tagging.<br>
Clear all tags of selected files with Backspace.<br>
##### Renaming tags
You can change all instances of an existing tag to a new tag name.
### Searching
Search comes in 3 modes. <br>
1) Default search is by filename. <br>
2) Separate tags with "|", if there are any "|" symbols search will be done by tags. Putting ! before the tag will remove the files containing it. Separating tags with ~ will choose files containing at least one of them. <br>
|A|B~C will select files with A|B, A|C, A|B|C;<br>
|A|!B|C will select files with A|C.<br>
3) Including "||" in the beginning will search for files with ONLY specified tags. Negative tag is not supported in this mode.
### Copying
You can copy images on Ctrl+C. Selected image will be pasted to clipboard. <br>
For gifs only the first frame is copied. <br>
Copying other files is not supported.