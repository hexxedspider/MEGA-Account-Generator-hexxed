import os
import sys
import subprocess

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def create_scheduled_task():
    script_dir = get_script_dir()
    signin_script = os.path.join(script_dir, 'signin_accounts.py')
    
    if not os.path.exists(signin_script):
        print(f"Error: signin_accounts.py not found at {signin_script}")
        return False
    
    task_name = "MEGA_WeeklyKeepAlive"
    python_exe = sys.executable
    
    print("\n" + "="*70)
    print("MEGA WEEKLY KEEP-ALIVE SCHEDULER")
    print("="*70 + "\n")
    
    print("This will create a scheduled task to run signin_accounts.py every week.")
    print("This helps keep your MEGA accounts active and prevents deletion.\n")
    
    xml_config = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Weekly MEGA account keep-alive task - logs into all accounts to prevent deletion due to inactivity</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T03:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Sunday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{signin_script}"</Arguments>
      <WorkingDirectory>{script_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    temp_xml = os.path.join(script_dir, 'mega_task_temp.xml')
    try:
        with open(temp_xml, 'w', encoding='utf-16') as f:
            f.write(xml_config)
        
        print("Creating scheduled task...")
        
        result = subprocess.run(
            ['schtasks', '/Create', '/TN', task_name, '/XML', temp_xml, '/F'],
            capture_output=True,
            text=True
        )
        
        if os.path.exists(temp_xml):
            os.remove(temp_xml)
        
        if result.returncode == 0:
            print("Scheduled task created successfully!\n")
            print("Task Details:")
            print(f"  Name:     {task_name}")
            print(f"  Schedule: Every Sunday at 3:00 AM")
            print(f"  Script:   {signin_script}")
            print(f"\nYou can view/modify this task in Windows Task Scheduler.")
            print("To disable: Open Task Scheduler and disable the task.")
            print(f"To remove: Run this script with --remove flag or use: schtasks /Delete /TN {task_name} /F")
            return True
        else:
            print("Failed to create scheduled task.")
            print(f"Error: {result.stderr}")
            print("\n" + "-"*70)
            print("MANUAL SETUP INSTRUCTIONS:")
            print("-"*70)
            print("1. Open Task Scheduler (search in Start menu)")
            print("2. Click 'Create Basic Task'")
            print(f"3. Name: {task_name}")
            print("4. Trigger: Weekly")
            print("5. Day: Sunday (or your preference)")
            print("6. Time: 3:00 AM (or your preference)")
            print("7. Action: Start a program")
            print(f"8. Program: {python_exe}")
            print(f"9. Arguments: \"{signin_script}\"")
            print(f"10. Start in: {script_dir}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if os.path.exists(temp_xml):
            os.remove(temp_xml)
        return False

def remove_scheduled_task():
    task_name = "MEGA_WeeklyKeepAlive"
    
    print("\n" + "="*70)
    print("REMOVING SCHEDULED TASK")
    print("="*70 + "\n")
    
    result = subprocess.run(
        ['schtasks', '/Delete', '/TN', task_name, '/F'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"Scheduled task '{task_name}' removed successfully!")
    else:
        print(f"Failed to remove task. It may not exist.")
        print(f"Error: {result.stderr}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['--remove', '-r', 'remove']:
        remove_scheduled_task()
    else:
        create_scheduled_task()
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
