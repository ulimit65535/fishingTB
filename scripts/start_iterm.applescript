on run argv
    set launchCommand to "exec /bin/bash " & quoted form of (item 1 of argv)
    repeat with argument in (rest of argv)
        set launchCommand to launchCommand & " " & quoted form of (contents of argument)
    end repeat

    tell application "iTerm"
        activate
        if (count of windows) is 0 then
            set targetWindow to (create window with default profile)
            set targetSession to current session of targetWindow
        else
            tell current window
                set targetTab to (create tab with default profile)
            end tell
            set targetSession to current session of targetTab
        end if
        tell targetSession to write text launchCommand
    end tell
end run
