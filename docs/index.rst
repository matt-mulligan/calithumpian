.. Calithumpian documentation master file, created by
   sphinx-quickstart on Sun Apr 19 08:44:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Calithumpian's documentation!
========================================
Calithumpian is a card game my family loves to play but we could not find a web client that had it. So i decided to make my own!
This project utilises Flask, SocketIO (via flask-socketIO) html, css and javascript to build out an interactive web app that plays calithumpian and can be hosted on any website.

What is Calithumpian?
---------------------
Calithumpian is a card game that my parents picked up from their friends after a weekend away.
It functions like hearts, if you ultimate goal in hearts was to actively annoy all your opponents more than to win.
Each round all players are dealt a hand of cards and a trump suit is selected. they must all say how many tricks they will win in that round and aim to win no more or no less.
each trick is decided by players playing a single card from their hand. The first player will play a card which determins the lead suit. if you have a card oif that suit you must play it. if not you can play a card of the trump suit to try and win the hand.
The winner of the previous hand leads the next hand.

.. toctree::
   :maxdepth: 4

	Calithumpian Module Docs <apidoc/modules.rst>
