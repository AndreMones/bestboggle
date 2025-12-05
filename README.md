# bestboggle
Find the highest scoring boggle boards possible

This project is ment to find really high scoring 5x5 boggle boards.

tools_boggle.py will let you score a board if you run it. The scoring function is abismaly slow, on account of it being written in python. My mom's c++ scoring function is like 32 times faster. This greatly slows down my ability to find high scoring boggle boards, but thanks to some clever optimization tricks, I think I've more than overcome this limitation.

create_boggle.py generates high scoring boards from random seeds, or it can refine a board you've already found.

when running create_boggle, you should also be running file_boggle.py in another tab. This code reads the boards that create_boggle finds, and stores them in a couple of files. Forgetting to run file_boggle doesn't cause any serious issues. But create_boggle will eventualy freeze until file_boggle get's run.

force quitting file_boggle with ctrl-c or another command may cause damage to boggle data files. Be sure to quit through the user prompt.

You can run also multiple instances of create_boggle.py at once, just make sure you assign them different request slots. DO NOT run multiple instances of file_boggle at once.

you can see all the boards I've found in data/boards/5x5.

you can see the boards you generate in "data/boards/5x5/compiled\ boards". You can also see the boards that I've found in "data/boards/5x5-Andre/compiled\ boards". You can also create new folders. You can control which folder the code operates on by editing BOARDS_FOLDER_PATH in config.py.

Can this code handle other board dimensions? I DON'T KNOW! I've never tested it. Theoreticaly It should work with any square board, as long as you make the change in config, but I never tested it. It probably wouldn't take much tweaking to make it work with non-square rectangular boards as well.