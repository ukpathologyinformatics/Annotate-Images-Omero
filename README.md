
# Annotate-Images-Omero
Annotate images using regions of interest (ROIs) from Omero using a Python script. Omero docs can be found at https://docs.openmicroscopy.org/omero/. 

# How to use
## Bring up your local Omero deployment
1. Open up a terminal, navigate to where you keep projects and stuff, and clone the Git repository for this project
2. Once that's done, you should have a "docker-compose.yml" file, this document (README.md), and a directory called "scripts."
3. Be sure you're in the root directory of the project, then bring up the containerized Omero servers by running "docker-compose up".
  * Watch the log output! Sometimes error messages will scroll by very quickly.
  * You won't be able to log into Omero right away, even though it appears to be fully operational. Login will fail in such a way that it looks like an incorrect password or something else, and the error message given is no help. 
  * You should see messages from the database instance (omero-db), the web and application server (omero-web), and the main Omero server (omero-server). The final messages should look like this:
    >omero-server   | Running /startup/99-run.sh 
	>omero-server   | Starting OMERO.server
  * You may have trouble accessing the Omero webclient from a remote machine. Why and how to fix it are out of the scope of this document (and I don't remember at the moment). I will update or address in a future version.


## Import an image
5. Open a fresh terminal window. Connect to the "omero-server" container using a command like this:
	`docker exec -it omero-server bash`
	Your prompt should change to:
	`bash-4.2$`
6. Get hold of an image to test with. I suggest using a whole-slide image like the sample here: ~~https://drive.google.com/open?id=14Rh6j2YJwbB3hIN1hyE4APEV1xStpWeZ~~. *** A test image should be uploaded as a .zip in the /scripts directory. Just unzip it and you're good to go.
7. ~~Copy the image to the directory that was bind-mounted to the container (./scripts).~~ (Should already be there). Go back to the terminal connected to the omero-server container and make sure you can see the image file from inside the container (/opt/scripts/test.svs).
9. In your terminal that's attached to the omero-server container, change directories to "/opt/omero/server/OMERO.server" and run the following command "./bin/omero". This should bring up the Omero Python shell. I might also refer to this as the "omero console" or "omero prompt." They're all the same thing. The output should look like this:
>OMERO Python Shell. Version 5.6.0
>Type "help" for more information, "quit" or Ctrl-D to exit
>omero>
  * You can also run a specific (Omero administration) command by adding it as an argument to ./bin/omero. For example, to list all of the Python scripts currently managed by Omero, you could type:
		`./bin/omero script list`
  * The help command is pretty useful here, as is the Omero documentation

10. From the omero prompt, type "import /opt/scripts/test.svs". It will prompt you for the server, username, and password to use for the Omero server connection. Use "localhost" for the server, "root" for the user, and "omero" for the password. 
* The Omero root password is set via an environment variable in the docker-compose.yml file.
* Some of the Omero commands may throw Java exceptions which trigger Python exceptions that cause the Omero shell to crash. For example, if you try to pass a bad path to "import," you'll see a bunch of error messages and be kicked back into the shell. If you're like me, you won't notice that it's errored out half of the time, so your next Omero command fails unexpectedly with an error message that is confusing at first.
11. You should see some text like this:
	Created session for root@localhost:4064. Idle timeout: 10 min. Current group: system
12. When finished, the import command will display a summary. Check to make sure that the expected number of files was uploaded (1 for the example) and that there weren't any errors. One file may contain multiple images, so there are separate counters for the number of images imported. **Stay in the Omero prompt for now, don't exit yet**
13. Open a web browser and point it at omero-web. If you didn't modify the docker-compose file, it'll be at http://localhost:4080. Log in using the root user and password as before.
14. You should see images in the "explore" pane on the left side of the browser window. They will be under "Orphaned Images" by default.
  * **NOTE**:Unexpected things can happen with permissions if you log in as someone other than root. For example, if you import images under one user (let's call him "dexter") and do not make the images visible to others, then when another user (let's say "baxter") logs in, she won't see any of dexter's images.

## Upload the script
15. You must import scripts into Omero, just like images. Switch back to your termimnal with the omero prompt in it and type "script list" to see all the scripts Omero knows about.
  * *Remember*: You can run any of these commands from the OS shell too. Just prefix them with "./bin/omero". Instead of typing "bin/omero \<ENTER\> script list", you could do "./bin/omero script list".
16. Upload your script by typing "script upload --official /opt/scripts/annotate.py". Note the "--official" option. It must come before the file path, and if you don't specify it, you won't be able to run your newly-uploaded script through the Omero Webclient. The Omero shell should say "Uploaded official script" followed by "OriginalFile:\<some number\>". Use "script list" again and confirm that your script was imported. Note the number, you'll need to pass it as a parameter when deleting or replacing the script.

## Manually Create ROIs (optional/old)
17. Next you will need some ROIs. In the Omero Webclient, open a (non-tiled) image. This should bring up the Omero iViewer (image viewer). There are several things to remember:
  * By default, Omero will refuse to export images larger than 12k x 12k pixels, so your ROIs must be smaller than that
  * **The user experience is a little weird with the Omero ROI tool. Pay attention to the quirks:**
   * Once you select the "ROI" tab and click the square in the bar with the different shapes, the next left click will set the location of the upper-left corner. Then you can drag the mouse pointer around to grow or shrink the area. Clicking again will set the lower right corner of the ROI.
   * It's easy to create new ROIs unintentionally. Use the "ROIs" section of the pane on the right side of the image viewer to help you keep them straight. If the comment you just entered isn't showing up on your ROI, check to make sure you didn't accidentally create a new one and set the comment on that.
   * You must click the "Save" button near the top-left part of the ROI tab to persist your changes to Omero. To make sure your ROIs saved, you should try closing and re-opening the image and see if the ROI is still there.
  * Prefix your tags with a "#" like the Twitters: "#MyTag" You can choose a different delimiter in the script options, but let's just keep it simple for now.

## Create ROIs with Python Script
18. Go back to the main Webclient window. There should be a "search" bar in the upper right corner. Next to this is a button with a funky-looking pentagon symbol, and next to that a button with some gears on it. Click on the image you want to add the ROI(s) to. It should be highlighted. Then, click the button with the gears and choose "opt" then "scripts" in the dropdown. You should see "annotate..". Click it!
19. A window with a description and parameters should open. The default arguments should work just fine. Click "Run" and watch the "Activites" dropdown that shows up.
20. When the script finishes, if everything went well, the "Activities" window should say "Finished Annotating". Now you can check the image to make sure the annotations have been created. * They should be in the top left corner if you are using the default values.

## Adding your own scripts or modifying the one provided
 * To add your own scripts or modify the ones provided, you can follow the same steps.
 * **NOTE**: You must re-upload the script for your changes to take effect, even if the path doesn't change. i.e. delete the old script using `script delete #`, then re-uploading.
