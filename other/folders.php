<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>THL Collab Wikis</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .banner {
            background-color: #cce5ff; /* light blue */
            padding: 20px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <h1>THL Collab Wikis</h1>
        </div>

        <ul class="list-group">
            <?php
            $dirs = array_filter(glob('*'), 'is_dir'); // get all subdirectories
            foreach ($dirs as $dir) {
                $homePage = $dir . '/wiki_'. $dir . '_Home.html';
                if (file_exists($homePage)) {
                    echo '<li class="list-group-item"><a href="' . htmlspecialchars($homePage) . '">' . htmlspecialchars($dir) . '</a></li>';
                }
            }
            ?>
        </ul>
    </div>

    <!-- Bootstrap JS (optional) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
