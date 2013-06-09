"""
A HN comment API based off of Scott Jackson's post API. 
======================================================

HNCommentAPI is released under the GPL V3:

Copyright (c) 2013, Kristopher Ruzic 
All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
"""






from BeautifulSoup import BeautifulSoup
import re

class HackerNewsCommentAPI(object):
    """
The class used for searching the HTML for all our comments and their data
"""
    numberOfComments = 0
    isTextPost = 0  # 0 means it is a text post. 1 means it isn't

    def getCommentText(self,source):
        """
Gets the comment text for a comment
"""
        textStart = source.find('font') + 21
        textEnd = source.find('</font', textStart)
        text = source[textStart:textEnd]
        text = re.sub('<[^<]+?>', '', text) # deletes all tags from the comment EX. links
        if text == '">[deleted]</span': # deleted comment signature
            text = '[deleted]'
        return text

    def getCommentIndent(self,source):
        """
Gets the comment's indent
"""
        indentStart = source.find('width=') + 7
        indentEnd = source.find('>', indentStart) - 3
        indent = source[indentStart:indentEnd]
        return indent

    def getCommentDetails(self, source):
        """
Gets the time & poster of a comment
"""
        posterStart = source.find('user?id=')
        realPosterStart = source.find('=', posterStart) + 1
        posterEnd = source.find('"', realPosterStart)
        poster = source[realPosterStart:posterEnd]
        if poster == '<span class=': # deleted comment signature
            poster = ''

        timeStart = source.find(poster + '</a>') + len(poster) + 5
        timeEnd = source.find('|', timeStart) - 1
        time = source[timeStart:timeEnd]
        if time == 'n class="comhead"></spa': # deleted comment signature
            time = ''

        return poster, time

    def getComments(self,source):
        """
Looks at the source, makes comments from it, and returns these comments
"""
        # Replaces <p> and <i> tags in the comments
        source = source.replace('<p>', '\n').replace('<i>', '').replace('</i>','')
        soup = BeautifulSoup(source)

        # gets the comment text
        comment_content = soup.findAll("span", {"class": "comment"})
        # gets the indent of the comment
        comment_indent = soup.findAll("img", {"src": "s.gif", "height": "1"})
        # gets the other info, ie) time and poster name
        comment_details = soup.findAll("span", {"class": "comhead"})
        # counts the number of comments
        self.numberOfComments = source.count('span class="comment"')

        if str(comment_details[0]).find('(') == 23: # link posts first result will actually be the domain name
            self.isTextPost = 1
        else:
            self.isTextPost = 0

        # Create an empty list of comments
        comments = []
        for i in range(0, self.numberOfComments):
            comment = HackerNewsComment()
            comments.append(comment)

        commentsText = []
        commentsIndent = []
        commentsIndentFinal = []
        commentsPoster = []
        commentsTime = []

        for c in range(0, len(comment_content)):
            comment = str(comment_content[c]) # turns the element into a string (changes it from a BeautifulSoup object)
            commentText = self.getCommentText(comment)
            commentsText.append(commentText)

        for h in range(1, len(comment_indent)): # The first comment is actually the second element of this list.
            comment = str(comment_indent[h])
            commentIndent = self.getCommentIndent(comment)
            if int(commentIndent) % 10 == 0: # if statement to remove the extra img tag deleted comments have
                commentsIndent.append(commentIndent)

        for s in range(self.isTextPost, len(comment_details)):
            comment = str(comment_details[s])
            poster, time = self.getCommentDetails(comment)
            commentsPoster.append(poster)
            commentsTime.append(time)

        # Merge these values to each represent one comment
        for i in range(0, self.numberOfComments):
            comments[i].commentNum = i + 1
            comments[i].text = commentsText[i]
            comments[i].indent = commentsIndent[i]
            comments[i].poster = commentsPoster[i]
            comments[i].timePosted = commentsTime[i]

        return comments

class HackerNewsComment:
    """
A class representing a comment on Hacker News
"""
    commentNum = 0
    text = ""
    indent = 0
    poster = ""
    timePosted = ""

    def printComments(self):
        """
Prints the details of the comment in xml format
"""
        print '\t\t<commentNum>', self.commentNum, '</commentNum>'
        print '\t\t<poster>' + self.poster + '</poster>'
        print '\t\t<timePosted>' + self.timePosted + '</timePosted>'
        print '\t\t<indent>' + self.indent + '</indent>'
        print '\t\t<text>' + self.text + '</text>'
