Gitmopy's Emoji Sets
=====================

.. toctree::
    :maxdepth: 2


Select your emoji sets from the command-line:

.. code-block:: bash

    $ gitmopy config

Gitmojis
--------

Default standard gitmojis are from `gitmoji.dev <https://gitmoji.dev/>`_.

.. literalinclude:: ../gitmopy/assets/gitmojis.yaml
    :language: yaml

AI-Devmojis
-----------

Alternative gitmojis tailored for AI/ML development. Suggestions are welcome, open a PR/issue on the `gitmopy repo <https://github.com/vict0rsch/gitmopy>`_.

.. literalinclude:: ../gitmopy/assets/ai_devmojis.yaml
    :language: yaml

Custom
------

You can also define your own emoji sets in a YAML file. Run ``gitmopy info`` to see the path to that custom emojis file on your system.

Custom emojis are loaded *after* the default emoji set you have selected (gitmojis or ai-devmojis). This means that you can override any emoji from the default set with your own custom emoji.
