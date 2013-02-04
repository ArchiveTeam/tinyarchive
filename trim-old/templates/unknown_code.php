<?
    $title = "Unknown Code";
    include("header.php");
?>
<h1>Unknown Code</h1>
<p>
    Unfortunately the original URL for http://tr.im/<?= View::escape($internal_code) ?> got lost when tr.im shut down. You can manually ask for the URL by contacting <a href="mailto:eric@ericwoodward.com">Eric Woodward</a>.
</p>
<? include("footer.php"); ?>
