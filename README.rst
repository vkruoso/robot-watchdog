Robot Watchdog
==============

|license|

.. |license| image:: https://img.shields.io/dub/l/vibe-d.svg?style=flat-square


Idea
----

The idea is to have a means to send data related to test execution in
Robot Framework to any interested party. With that information one can
handle the data as it likes. Some exemples include displaying a real-time
dashboard and storing it in a database for further analisys.

Usage::

    $ pybot --listener robotwatchdog tests/
