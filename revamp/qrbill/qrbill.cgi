#!/usr/bin/perl

use strict;
use warnings;
use lib qw(lib /home/sts/perl5/lib/perl5/x86_64-linux-gnu-thread-multi);

use CGI;
#use CGI::Carp 'fatalsToBrowser';
use Data::Dumper;
use SL::Helper::QrBill;

my @html = split /\n###\n/, do { local $/; <DATA> };

my $query = CGI->new;

my $action = $query->param('action');

if ($action eq 'generate') {
  my %h;
  foreach my $param ($query->param) {
     $h{$param} = $query->param($param);
  }
  my @hrefs = (
    { iban => $h{biller_iban} },
    { address_type => $h{biller_address_type},
      company => $h{biller_company},
      address_row1 => $h{biller_address_row1},
      address_row2 => $h{biller_address_row2},
      street => $h{biller_street},
      street_no => $h{biller_street_no},
      postalcode => $h{biller_postalcode},
      city => $h{biller_city},
      countrycode => $h{biller_countrycode} },
    { amount => $h{payment_amount},
      currency => $h{payment_currency} },
    { address_type => $h{recipient_address_type},
      name => $h{recipient_name},
      address_row1 => $h{recipient_address_row1},
      address_row2 => $h{recipient_address_row2},
      street => $h{recipient_street},
      street_no => $h{recipient_street_no},
      postalcode => $h{recipient_postalcode},
      city => $h{recipient_city},
      countrycode => $h{recipient_countrycode} },
    { type => $h{ref_nr_type},
      ref_number => $h{ref_nr_number} },
    { unstructured_message => $h{additional_unstructured_message} },
  );
  eval { SL::Helper::QrBill->new(@hrefs)->generate(); };
  if ($@) {
    form($@);
  }
  else {
    print <<"HTML";
Content-Type: text/html

$html[1]
HTML
  }
}
else {
  form();
}

sub subst_regex
{
  my ($html, $place_holder, $regex) = @_;

  local $Data::Dumper::Terse = 1;
  local $Data::Dumper::Varname = '';

  my $dumper = Dumper($regex);
  chomp $dumper;

  $$html =~ s/\$$place_holder/$dumper/;
}

sub form
{
  my ($error) = @_;

  chomp $error;
  my $html = $html[0];

  $html =~ s/\$ERROR/$error/;
  $html =~ s/\$VERSION/$SL::Helper::QrBill::VERSION/;

  my %regexes = SL::Helper::QrBill::_get_regexes();

  subst_regex(\$html, 'BILLER_IBAN1', $regexes{'biller information'}->[0][1]);
  subst_regex(\$html, 'BILLER_IBAN2', $regexes{additional}{qr_iban});

  subst_regex(\$html, 'BILLER_ADDRESS_TYPE', $regexes{'biller data'}->[0][1]);
  subst_regex(\$html, 'BILLER_COMPANY', $regexes{'biller data'}->[1][1]);
  subst_regex(\$html, 'BILLER_ADDRESS_ROW1', $regexes{'biller data'}->[2][1]);
  subst_regex(\$html, 'BILLER_ADDRESS_ROW2', $regexes{'biller data'}->[3][1]);
  subst_regex(\$html, 'BILLER_STREET', $regexes{'biller data'}->[4][1]);
  subst_regex(\$html, 'BILLER_STREET_NO', $regexes{'biller data'}->[5][1]);
  subst_regex(\$html, 'BILLER_POSTALCODE', $regexes{'biller data'}->[6][1]);
  subst_regex(\$html, 'BILLER_CITY', $regexes{'biller data'}->[7][1]);
  subst_regex(\$html, 'BILLER_COUNTRYCODE', $regexes{'biller data'}->[8][1]);

  subst_regex(\$html, 'PAYMENT_AMOUNT', $regexes{'payment information'}->[0][1]);
  subst_regex(\$html, 'PAYMENT_CURRENCY', $regexes{'payment information'}->[1][1]);

  subst_regex(\$html, 'RECIPIENT_ADDRESS_TYPE', $regexes{'invoice recipient data'}->[0][1]);
  subst_regex(\$html, 'RECIPIENT_NAME', $regexes{'invoice recipient data'}->[1][1]);
  subst_regex(\$html, 'RECIPIENT_ADDRESS_ROW1', $regexes{'invoice recipient data'}->[2][1]);
  subst_regex(\$html, 'RECIPIENT_ADDRESS_ROW2', $regexes{'invoice recipient data'}->[3][1]);
  subst_regex(\$html, 'RECIPIENT_STREET', $regexes{'invoice recipient data'}->[4][1]);
  subst_regex(\$html, 'RECIPIENT_STREET_NO', $regexes{'invoice recipient data'}->[5][1]);
  subst_regex(\$html, 'RECIPIENT_POSTALCODE', $regexes{'invoice recipient data'}->[6][1]);
  subst_regex(\$html, 'RECIPIENT_CITY', $regexes{'invoice recipient data'}->[7][1]);
  subst_regex(\$html, 'RECIPIENT_COUNTRYCODE', $regexes{'invoice recipient data'}->[8][1]);

  subst_regex(\$html, 'REF_NR_TYPE', $regexes{'reference number data'}->[0][1]);
  subst_regex(\$html, 'REF_NR_NUMBER', $regexes{additional}{ref_nr});

  subst_regex(\$html, 'ADDITIONAL_UNSTRUCTURED_MESSAGE', $regexes{'additional information'}->[0][1]);

  print <<"HTML";
Content-Type: text/html

$html
HTML
}

__DATA__
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    <link rel="stylesheet" type="text/css" href="qrbill.css">
    <title>QrBill.pm Generator</title>
    <script>
      function reset_form() {
          document.getElementById('error').innerHTML = '';
      }
    </script>
  </head>
  <body>
    <form method="post" accept-charset="utf-8" action="./">
      <input type="hidden" name="action" value="generate">
      <h3><a href="https://github.com/kivitendo/kivitendo-erp/blob/master/SL/Helper/QrBill.pm" target="_blank">QrBill.pm</a> Generator <code>(v$VERSION)</code></h3>
      <table>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
        <tr>
          <td colspan="3"><b>biller information</b></td>
        </tr>
        <tr>
          <td class="td">IBAN:</td><td><input type="text" name="biller_iban" value=""></td><td class="code"><code>$BILLER_IBAN1<br>$BILLER_IBAN2 (QRR)</code></td>
        </tr>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
        <tr>
          <td colspan="3"><b>biller data</b></td>
        </tr>
        <tr>
          <td class="td">Address Type:</td><td>K <input type="radio" name="biller_address_type" value="K"> S <input type="radio" name="biller_address_type" value="S"></td><td class="code"><code>$BILLER_ADDRESS_TYPE</code></td>
        </tr>
        <tr>
          <td class="td">Company:</td><td><input type="text" name="biller_company" value=""></td><td class="code"><code>$BILLER_COMPANY</code></td>
        </tr>
        <tr>
          <td class="td">Address Row1:</td><td><input type="text" name="biller_address_row1" value=""></td><td class="code"><code>$BILLER_ADDRESS_ROW1</code></td>
        </tr>
        <tr>
          <td class="td">Address Row2:</td><td><input type="text" name="biller_address_row2" value=""></td><td class="code"><code>$BILLER_ADDRESS_ROW2</code></td>
        </tr>
        <tr>
          <td class="td">Street:</td><td><input type="text" name="biller_street" value=""></td><td class="code"><code>$BILLER_STREET</code></td>
        </tr>
        <tr>
          <td class="td">Street No:</td><td><input type="text" name="biller_street_no" value=""></td><td class="code"><code>$BILLER_STREET_NO</code></td>
        </tr>
        <tr>
          <td class="td">Postalcode:</td><td><input type="text" name="biller_postalcode" value=""></td><td class="code"><code>$BILLER_POSTALCODE</code></td>
        </tr>
        <tr>
          <td class="td">City:</td><td><input type="text" name="biller_city" value=""></td><td class="code"><code>$BILLER_CITY</code></td>
        </tr>
        <tr>
          <td class="td">Countrycode:</td><td><input type="text" name="biller_countrycode" value=""></td><td class="code"><code>$BILLER_COUNTRYCODE</code></td>
        </tr>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
        <tr>
          <td colspan="3"><b>payment information</b></td>
        </tr>
        <tr>
          <td class="td">Amount:</td><td><input type="text" name="payment_amount" value=""></td><td class="code"><code>$PAYMENT_AMOUNT</code></td>
        </tr>
        <tr>
          <td class="td">Currency:</td><td><select name="payment_currency"><option selected>CHF</option><option>EUR</option></select></td><td class="code"><code>$PAYMENT_CURRENCY</code></td>
        </tr>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
        <tr>
          <td colspan="3"><b>invoice recipient data</b></td>
        </tr>
        <tr>
          <td class="td">Address Type:</td><td>K <input type="radio" name="recipient_address_type" value="K"> S <input type="radio" name="recipient_address_type" value="S"></td><td class="code"><code>$RECIPIENT_ADDRESS_TYPE</code></td>
        </tr>
        <tr>
          <td class="td">Name:</td><td><input type="text" name="recipient_name" value=""></td><td class="code"><code>$RECIPIENT_NAME</code></td>
        </tr>
        <tr>
          <td class="td">Address Row1:</td><td><input type="text" name="recipient_address_row1" value=""></td><td class="code"><code>$RECIPIENT_ADDRESS_ROW1</code></td>
        </tr>
        <tr>
          <td class="td">Address Row2:</td><td><input type="text" name="recipient_address_row2" value=""></td><td class="code"><code>$RECIPIENT_ADDRESS_ROW2</code></td>
        </tr>
        <tr>
          <td class="td">Street:</td><td><input type="text" name="recipient_street" value=""></td><td class="code"><code>$RECIPIENT_STREET</code></td>
        </tr>
        <tr>
          <td class="td">Street No:</td><td><input type="text" name="recipient_street_no" value=""></td><td class="code"><code>$RECIPIENT_STREET_NO</code></td>
        </tr>
        <tr>
          <td class="td">Postalcode:</td><td><input type="text" name="recipient_postalcode" value=""></td><td class="code"><code>$RECIPIENT_POSTALCODE</code></td>
        </tr>
        <tr>
          <td class="td">City:</td><td><input type="text" name="recipient_city" value=""></td><td class="code"><code>$RECIPIENT_CITY</code></td>
        </tr>
        <tr>
          <td class="td">Countrycode:</td><td><input type="text" name="recipient_countrycode" value=""></td><td class="code"><code>$RECIPIENT_COUNTRYCODE</code></td>
        </tr>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
        <tr>
          <td colspan="3"><b>reference number data</b></td>
        </tr>
        <tr>
          <td class="td">Type:</td><td><select name="ref_nr_type"><option selected>QRR</option><option>NON</option></select></td><td class="code"><code>$REF_NR_TYPE</code></td>
        </tr>
        <tr>
          <td class="td">Ref Number:</td><td><input type="text" name="ref_nr_number" value=""></td><td class="code"><code>$REF_NR_NUMBER</code></td>
        </tr>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
        <tr>
          <td colspan="3"><b>additional information</b></td>
        </tr>
        <tr>
          <td class="td">Unstructured Message:</td><td><textarea name="additional_unstructured_message" rows="1"></textarea></td><td class="code"><code>$ADDITIONAL_UNSTRUCTURED_MESSAGE</code></td>
        </tr>
        <tr>
          <td colspan="3"><hr></td>
        </tr>
      </table>
      <font color="red" id="error">$ERROR</font><br>
      <input type="submit" value="generate"> <input type="reset" value="reset" onclick="reset_form()"><br>
    </form>
  </body>
</html>
###
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    <link rel="stylesheet" type="text/css" href="qrbill.css">
    <title>QrBill.pm Generator</title>
  </head>
  <body>
    <img src="out.png"><br><br>
    <a href="javascript:history.back()">return</a>
  </body>
</html>
