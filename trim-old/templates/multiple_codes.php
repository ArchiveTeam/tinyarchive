<?
    $title = "Multiple URLs";
    include("header.php");
?>
<h1>Multiple URLs known</h1>
<p>
    Please clarify which tr.im shorturl you wanted to visit:
</p>
<ul>
    <? foreach($rows as $row): ?>
        <li><a href="<?= View::escape($row[1]) ?>">http://tr.im/<?= View::escape($row[0]) ?></a></li>
    <? endforeach; ?>
</ul>
<? include("footer.php"); ?>
