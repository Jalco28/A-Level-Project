<html>
<body>

<?php

    $username = $_POST["username"];
    $score = $_POST["score"];
    $difficulty = $_POST["difficulty"];
    $date = $_POST["date"];
    $actual_user  = $_POST["actual_user"];
    shell_exec("python3 /var/www/html/doorsos/new.py $username $score $difficulty $date $actual_user")

?>

</body>
</html>
