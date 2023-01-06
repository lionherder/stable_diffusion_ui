Safe place to drop my stable diffusion UI code

This is a UI frontend to the Stable Diffusion Web UI rest api written by [Automatic111](https://github.com/AUTOMATIC1111/stable-diffusion-webui).  Getting that up and running is all on you.

It provides a session-based interface to SD instead of the single-user experience of the Stable Diffusion Web UI.  Meaning, you can share it with friends.

The interface is geared towards fun and sharing of images.  Anonymous as you like.  Security through obscurity.  Database integration.

Changes notes:

V1.0:

  * Retro: Used shelve as my persistent object database which was made of fail.  Corrupted all the time under load.
  * Retro: Needed to separate controller/model code more cleanly.

V1.1:

  * Dropped shelve in place of using a sqlite.  Shelve is very unstable and corrupts frequently under load
    * All the urls to images use a hash which is computed at INSERT time.  New hash means 404's for old links.
  * Split up the entire model/controll code mess.  Didn't touch the views much at all.
  * New Playground page
  * Prompt info stored with image
  * Info hover over images shows detailed information about it.
    * Controlled by show_owner and show_info boolean fields
    * Full info only shows for owner of the picture
  * Added 404_page, view image page
  * So many tweaks
  
  * Next: Bio Page -- Display name and bio, stats
  * Next: Edit picture permissions page
  
V1.2:
  * Update profile page
    * Edit bio and display name
    * Use a display name to keep the user id off the page header.  Was a little secuity concern when screen sharing.
  * Edit images and edit image properties page
    * The info that is displayed on image hover by other users can be controlled
    * Title - If present, will always be displayed with the image.  Leave blank to disable.
    * Show Owner - Shows the owner name of a file.  Your display name, not your user id.
    * Show Info - Shows meta data on the file, things like params for your image generation.
  * Page caching for speed instead of direct DB access.
  * Controllers
    * Created page, user and image item controller classes
    * Create model managers/controllers
  * Lots of clean up and consistency updates
  * Small DB migration
  * Added logging
