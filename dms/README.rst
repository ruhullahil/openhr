==========================
Document Management System
==========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:904150d6b7037648a3ed02450c9b27d802f4cee614b59b1fa582f48093e1a0ed
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fdms-lightgray.png?logo=github
    :target: https://github.com/OCA/dms/tree/18.0/dms
    :alt: OCA/dms
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/dms-18-0/dms-18-0-dms
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/dms&target_branch=18.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

DMS is a module for creating, managing and viewing document files
directly within Odoo. This module is only the basis for an entire
ecosystem of apps that extend and seamlessly integrate with the document
management system.

This module adds portal functionality for directories and files for
allowed users, both portal or internal users. You can get as well a
tokenized link from a directory or a file for sharing it with any
anonymous user.

**Table of contents**

.. contents::
   :local:

Installation
============

Preview
-------

``python-magic`` library is recommended to be installed for having whole
support to get proper file types and file preview.

Configuration
=============

Configuration
=============

To configure this module, you need to:

1. Create a storage
-------------------

1. Go to *Documents -> Configuration -> Storages*.

2. Create a new document storage. You can choose between three options
   on ``Save Type``:

   - ``Database``: Store the files on the database as a field
   - ``Attachment``: Store the files as attachments
   - ``File``: Store the files on the file system

2. Create an access group
-------------------------

1. Next, create an administrative access group. Go to *Configuration ->
   Access Groups*.

   - Create a new group, name it appropriately, and turn on all three
     permissions (Create, Write and Unlink. Read is implied and always
     enabled).
   - Add any other top-level administrative users to the group if needed
     (your user should already be there).
   - You can create other groups in here later for fine-grained access
     control.

3. Create a directory
---------------------

1. Afterward, go to *Documents -> Directories*.

2. Create a new directory, mark it as root and select the previously
   created setting.

   - Select the *Groups* tab and add your administrative group created
     above. If your directory was already created before the group, you
     can also add it in the access groups (*Configuration -> Access
     Groups*).

3. In the directory settings, you can also add other access groups
   (created above) that will be able to:

   - read
   - create
   - write
   - delete

Migration
=========

If you need to modify the storage ``Save Type`` you might want to
migrate the file data. To achieve it, you need to:

1. Go to *Documents -> Configuration -> Storage* and select the storage
   you want to modify
2. Modify the save type
3. Press the button Migrate files if you want to migrate all the files
   at once
4. Press the button Manual File Migration to specify files one by one

You can check all the files that still need to be migrated from all
storages and migrate them manually on *Documents -> Configuration ->
Migration*

File Wizard Selection
=====================

There is an action called ``action_dms_file_wizard_selector`` to open a
wizard to list files in kanban view. This can be used (example
dms_attachment_link module) to add a button in kanban view with the
action we need.

Usage
=====

The best way to manage the documents is to switch to the Documents view.
Existing documents can be managed there and new documents can be
created.

Portal functionality
--------------------

You can add any portal user to DMS access groups, and then allow that
group in directories, so they will see in the portal such directories
and their files. Another possibility is to click on "Share" button
inside a directory or a file for obtaining a tokenized link for single
access to that resource, no matter if logged or not.

Known issues / Roadmap
======================

- Files preview in portal
- Allow to download folder in portal and create zip file with all
  content
- Save in cache own_root directories and update in every
  create/write/unlink function
- Add a migration procedure for converting an storage to attachment one
  for populating existing records with attachments as folders
- Add a link from attachment view in chatter to linked documents
- If Inherit permissions from related record (the
  inherit_access_from_parent_record field from storage) is changed when
  directories already exist, inconsistencies may occur because groups
  defined in the directories and subdirectories will still exist, all
  groups in these directories should be removed before changing.
- Since portal users can read ``dms.storage`` records, if your module
  extends this model to another storage backend that needs using
  secrets, remember to forbid access to the secrets fields by other
  means. It would be nice to be able to remove that rule at some point.
- Searchpanel in files: Highlight items (shading) without records when
  filtering something (by name for example).
- Accessing the clipboard (for example copy share link of
  file/directory) is limited to secure connections. It also happens in
  any part of Odoo.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/dms/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/dms/issues/new?body=module:%20dms%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* MuK IT
* Tecnativa

Contributors
------------

- Mathias Markl <mathias.markl@mukit.at>
- Enric Tobella <etobella@creublanca.es>
- Antoni Romera
- Gelu Boros <gelu.boros@rgbconsulting.com>
- `Tecnativa <https://www.tecnativa.com>`__:

  - Víctor Martínez
  - Pedro M. Baeza
  - Jairo Llopis

- `Elego <https://www.elegosoft.com>`__:

  - Yu Weng <yweng@elegosoft.com>
  - Philip Witte <phillip.witte@elegosoft.com>
  - Khanh Bui <khanh.bui@mail.elegosoft.com>

- `Subteno <https://www.subteno.com>`__:

  - Timothée Vannier <tva@subteno.com>

- `Kencove <https://www.kencove.com>`__:

  - Mohamed Alkobrosli <malkobrosly@kencove.com>

Other credits
-------------

Some pictures are based on or inspired by:

- `Roundicons <https://www.flaticon.com/authors/roundicons>`__
- `Smashicons <https://www.flaticon.com/authors/smashicons>`__
- `EmojiOne <https://github.com/EmojiTwo/emojitwo>`__ : Portal DMS icon
- `GitHub Octicons <https://github.com/primer/octicons/>`__ : The main
  DMS icon

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/dms <https://github.com/OCA/dms/tree/18.0/dms>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
