<html>
<body>

<?php

    $username = $_POST["username"];
    shell_exec("python3 /var/www/html/doorsos/delete.py '$username'")

?>

</body>
</html>
