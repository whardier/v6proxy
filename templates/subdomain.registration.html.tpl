{% extends 'navigation.html.tpl' %}

{% block content %}
<div class="jumbotron">
    <div class="container">
        <h1>Registration Status</h1>
        {% if status == 'email-sent' %}
            <p>There don't appear to be any subdomain conflicts and an e-mail has been sent to you that has an <b>activation link</b> inside.  Mayhaps you should check your e-mail?<p>
            <br/>
            <p style='text-align: center'>
                <i class="fa fa-envelope fa-spin" style="font-size: 5em; opacity: 0.25;"></i>
            </p>
            <br/>
            <p>If you don't see an activation e-mail please remember to check your spam folder.  Lastly you may simply refresh this page to resend the e-mail.</p>
        {% elif status == 'not-latest-or-in-time' %}
            <p>There are some subdomain conflicts.  Consult the <a href="{{ reverse_url('faq') }}">F.A.Q.</a> for what to do when there is a subdomain conflict on registration.<p>
            <br/>
            <p style='text-align: center'>
                <i class="fa fa-clock-o fa-spin" style="font-size: 5em; opacity: 0.25;"></i>
            </p>
        {% end %}
    </div>
</div>

{% end %}
