<html>
<body>

<?php

    $username = $_POST["username"];
    $score = $_POST["score"];
    $difficulty = $_POST["difficulty"];
    $date = $_POST["date"];
    shell_exec("python3 /var/www/html/doorsos/new.py $username $score $difficulty $date")

?>

</body>
</html>
