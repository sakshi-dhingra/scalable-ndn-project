# Setup Details

0. scp <from> <to> # to send from laptop to macneill

   scp -r Downloads/<foldername> dhingras@macneill.scss.tcd.ie:~/

1. ssh dhingras@macneill.scss.tcd.ie

2. ssh dhingras@rasp-043.berry.scss.tcd.ie



3. ip a    # to find ip of Rpi

   A - 10.35.70.43
   B - 


4. ps # get running processes

5. killall python3 # kill all python3 processes

6. kill -9 <pid> # kill process by pid

7. ss -tlnp # to check open ports


## To run the script
<open folder location>
8. python3 main.py 

burtond@rasp-010:~$ source prj3env/bin/activate
(prj3env) burtond@rasp-010:~$

dhingras@rasp-043:~$ source prj3env/bin/activate
(prj3env) dhingras@rasp-043:~$