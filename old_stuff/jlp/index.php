<html>
<head>
<title>PHP Form Handling</title>
<style>
    body{
        font-size: larger;
        font-family: arial;
        text-align: center;
        margin: 5vw;
        background-color: black;
        color: white;^
    }
    input{
        border-radius: 5vw;
        width: 13vw;
        height: 2vw;
        padding: 3vw;
    }
    textarea{
        height: 10vw;
        width: 20vw;
    }
    button{
        background-color: red;
        border-radius: 5vw;
        color: white;
        width: 5vw;
        height: 3vw;
    }
</style>
</head>

<body>
    <main>
        <p style="font-size: 3vw;">Send E-Mail</p>
        <form action="contactform.php" method="form" class="contactForm"></form>
            <input type="text" name="name" placeholder="Full Name"><br><br><br>
            <input type="text" name="mail" placeholder="Your E-Mail"><br><br><br>
            <input type="text" name="subject" placeholder="subject"><br><br><br>
            <textarea name="message" id="" placeholder="message"></textarea><br><br><br>
            <button type="submit" name="submit"><b>Send Mail</button>
    </main>

</body>
</html>

<?php

?>