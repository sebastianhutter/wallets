<!doctype html>

<html lang="en">
  <head>
    <meta charset="utf-8">

    <title>Wallets Overview</title>

    <style>
      body {
        background-color: linen;
      }

      h1 {
        color: maroon;
        margin-left: 40px;
      }
      table {
        border-collapse: collapse;
      }

      table, th, td {
        border: 1px solid black;
        text-align: left;
        padding: 0.2em;
      }

      tr.title {
        background-color: #f0f5f5;
      }

      tr.ok {
        background-color: #64FE2E;
      }
    </style>

    <link
        href="https://cdn.pydata.org/bokeh/release/bokeh-0.12.6.min.css"
        rel="stylesheet" type="text/css">
    <link
        href="https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.6.min.css"
        rel="stylesheet" type="text/css">

    <script src="https://cdn.pydata.org/bokeh/release/bokeh-0.12.6.min.js"></script>
    <script src="https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.6.min.js"></script>

  </head>

  <body>
    <h1>Wallets Overview</h1>

    % for exchange in data['exchanges']:
    <h2>{{exchange['name']}}</h2>
    <p>
      {{!exchange['coin_graph']['script']}}
      {{!exchange['coin_graph']['div']}}
    </p>
    <p>
      {{!exchange['rate_graph']['script']}}
      {{!exchange['rate_graph']['div']}}
    </p>
    <p>
      {{!exchange['euro_graph']['script']}}
      {{!exchange['euro_graph']['div']}}
    </p>
    <table>
      <tr class="title">
        <th>Timestamp</th>
        <th>Wallet Type</th>
        <th>Currency</th>
        <th>Balance</th>
        <th>Balance in EURO</th>
      </tr>
      % for wallet in exchange['wallets']:
      <tr>
        <td>{{wallet['timestamp']}}</td>
        <td>{{wallet['type']}}</td>
        <td>{{wallet['currency']}}</td>
        <td>{{wallet['balance']}}</td>
        <td>{{wallet['balance_euro']}}</td>
      </tr>
      % end
      <tr>
        <td colspan="4">Total</td>
        <td>{{exchange['total']}}</td>
      </tr>
    </table>
    % end
  </body>
</html>