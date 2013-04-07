#!/usr/bin/python2.4
# -*- encoding: latin1 -*-
#
# Copyright 2006 Google Inc. All Rights Reserved.

"""Test the dot2svg code
"""
__author__ = 'scottkirkwood@google.com (Scott Kirkwood)'

import dot2svg
import unittest
import os
import re
import difflib

def CompareFiles(new_file, correct_file):
    d = difflib.Differ()
    new_text = open(new_file).read().splitlines(1)
    correct_text = open(correct_file).read().splitlines(1)
    diffs = list(d.compare(new_text, correct_text))
    for diff in diffs:
      if diff[0:2] != '  ':
        print diff

class FollowUrlTest(unittest.TestCase):
  def testFloat(self):
     re_float = re.compile(dot2svg.regfloat)
     self.assertTrue(re_float.match('0'))
     self.assertTrue(re_float.match('-0'))
     self.assertTrue(re_float.match('-36'))
     self.assertTrue(re_float.match('1.421'))
     self.assertTrue(re_float.match('-1'))
     self.assertTrue(re_float.match('.123e-12'))

  def testRemoveWhiteBackground(self):
    text = ('<polygon style="fill:white;stroke:white;" '
            'points="54,-36 1.42109e-14,-36 0,-1.42109e-14 54,-0 54,-36"/>')
    self.assertEqual('', dot2svg.RemoveWhiteBackground(text))
    text = ('<polygon somthing="else" style="fill:white; stroke:white;" '
            'points="54,-36 1.42109e-14,-36 0,-1.42109e-14 54,-0 54,-36"/>')
    self.assertEqual('', dot2svg.RemoveWhiteBackground(text))
    text = ('<polygon \n style="fill:white; stroke:white;" '
            'points="54,-36 1.42109e-14,-36 0,-1.42109e-14 54,-0 54,-36"/>')
    self.assertEqual('', dot2svg.RemoveWhiteBackground(text))

  def testPolygonToRext(self):
    text = ('<polygon style="fill:lightgrey;stroke:black;" '
            'points="54,-36 1.42109e-14,-36 0,-1.42109e-14 54,-0 54,-36"/>')

    result = dot2svg.PolygonToRect(text)
    self.assertEqual(('<rect style="fill:lightgrey;stroke:black;" '
                      'x="0" y="-36" width="54" height="36" rx="5" ry="5"/>'), result)
    text = ('<polygon style="fill:lightgrey" '
            'points="232,14 138,14 138,50 232,50 232,14"/>')
    result = dot2svg.PolygonToRect(text)
    self.assertEqual(('<rect style="fill:lightgrey" '
    	'x="138" y="14" width="94" height="36" rx="5" ry="5"/>'), result)

  def testAddShadows(self):
    text = ('<rect style="bob;" />')
    result = dot2svg.AddShadows(text)
    self.assertEqual(('<rect fill="#999999" stroke="#999999" stroke-width="1" '
        'transform="translate(2, 2)" style="opacity:0.75;filter:url(#filterBlur)"  />'
        '\n<rect style="bob;" />'), result)


  def testFixFontSize(self):
    text = 'font-size:14.0;'
    result = dot2svg.FixFont(text)
    self.assertEqual('font-size:12px;', result)

  def testStrToTuple(self):
    self.assertEqual((2, 3), dot2svg.StrToTuple('(2, 3)'))
    self.assertEqual(None, dot2svg.StrToTuple(''))
    self.assertEqual((-1, 1.2), dot2svg.StrToTuple('(-1, 1.2)'))
    self.assertEqual((1, 2), dot2svg.StrToTuple((1, 2)))

if __name__ == '__main__':
  unittest.main()
