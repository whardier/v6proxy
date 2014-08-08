{% extends 'navigation.html.tpl' %}

{% block content %}
<div class="jumbotron">
    <div class="container">
        <h1>Registration Activation Status</h1>
        {% if status == 'ok' %}
            <p>There don't appear to be any problems so I'm going to assume you have dig at your disposal and can check things out!</p>
            <br/>
            <p style='text-align: center'>
                <i class="fa fa-beer fa-spin" style="font-size: 5em; opacity: 0.25;"></i>
            </p>
            <br/>
            <p>If you don't see an activation e-mail please remember to check your spam folder.  Lastly you may simply refresh this page to resend the e-mail.</p>
        {% elif status == 'error' %}
            <p>There was an error and we're getting to a point soon where those errors will start making sense to people.</p>
            <br/>
            <p style='text-align: center'>
                <i class="fa fa-bomb fa-spin" style="font-size: 5em; opacity: 0.25;"></i>
            </p>
        {% end %}
    </div>
</div>

{% end %}
