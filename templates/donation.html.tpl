{% extends 'navigation.html.tpl' %}

{% block content %}
<div class="jumbotron">
    <div class="container">
        <!-- Main component for a primary marketing message or call to action -->
        <h1><a href="http://en.wikipedia.org/w/index.php?title=There_ain%27t_no_such_thing_as_a_free_lunch&oldid=618732896">T.A.N.S.T.A.A.F.L.</a></h1>
        <hr/>
        <p>
            <a href="http://v6proxy.com">
                <b>v6proxy</b>
            </a>
            provides services beyond the
            <a href="http://cloudflare.com">
                <b>CloudFlare</b>
            </a>
            Free Plan on each domain available for subdomain registration which adds up.  If you use the service and like it, consider donating so that it stays up for as long as possible.  You can do a single or monthly donation through PayPal, a single donation through Dwolla, or email me about where to send any other payment methods.
        </p>

<br/>
<br/>

        <div class="row">

            <div class="col-md-4">

                <div class="panel panel-default">
                    <div class="panel-heading">via PayPal</div>
                    <div class="panel-body" style="text-align: center;">
                        Click the button below or send donations to <b>spencersr@brutetech.com</b> via PayPal
                        <br/>
                        <br/>

                        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
                            <input type="hidden" name="cmd" value="_s-xclick">
                            <input type="hidden" name="hosted_button_id" value="Q3JEEDGACX2HN">
                            <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
                            <img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
                        </form>

                        <br/>
                    </div>
                </div>

            </div>
            <div class="col-md-4">

                <div class="panel panel-default">
                    <div class="panel-heading">via Dwolla</div>
                    <div class="panel-body" style="text-align: center;">
                        Select an amount and click the button below or send donations to <b>spencersr@brutetech.com</b> via Dwolla
                        <br/>
                        <br/>
    
                        <script
                          src="https://www.dwolla.com/scripts/button.min.js" class="dwolla_button" type="text/javascript"
                          data-key="kPfbovobTFk8pptdCwYlsBNs/HBDOLxdgZ5eicZ1ad7ulVVkOC"
                          data-redirect="http://v6proxy.com/"
                          data-label="Donate via Dwolla"
                          data-name="v6proxy"
                          data-description="IPv4/IPv6 to IPv6"
                          data-amount="5.00"
                          data-guest-checkout="true"
                          data-type="freetype"
                        >
                        </script>
    
                        <br/>
                    </div>
                </div>

            </div>
            <div class="col-md-4">

                <div class="panel panel-default">
                    <div class="panel-heading">via Other</div>
                    <div class="panel-body" style="text-align: center;">
                        Send <b><a href="mailto:spencersr@brutetech.com">spencersr@brutetech.com</a></b> any questions you have on donations, how they are put to use, and where to send cash or check donations.
                        <br/>
                    </div>                
                </div>
                
            </div>
        </div>
    </div>
</div>

{% end %}
