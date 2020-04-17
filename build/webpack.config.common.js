'use strict';

const VueLoaderPlugin = require('vue-loader/lib/plugin');
const HtmlPlugin = require('html-webpack-plugin');
const MiniCSSExtractPlugin = require('mini-css-extract-plugin');
const Dotenv = require('dotenv-webpack');
const helpers = require('./helpers');
const isDev = process.env.NODE_ENV !== 'production';

const webpackConfig = {
  entry: {
    main: helpers.root('src', 'clientEntry'),
  },
  output: {
    path: helpers.root('dist'),
    publicPath: '/',
    filename: 'js/[name].js',
  },
  resolve: {
    extensions: ['.js', '.vue'],
    alias: {
      'vue$': isDev ? 'vue/dist/vue.runtime.js' : 'vue/dist/vue.runtime.min.js',
      '@': helpers.root('src')
    }
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        include: [helpers.root('src')]
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        include: [helpers.root('src')]
      },
      {
        test: /\.css$/,
        use: [
          isDev ? 'vue-style-loader' : MiniCSSExtractPlugin.loader,
          { loader: 'css-loader', options: { sourceMap: true } },
        ]
      },
      {
        test: /\.scss$/,
        use: [
          isDev ? 'vue-style-loader' : MiniCSSExtractPlugin.loader,
          { loader: 'css-loader', options: { sourceMap: true } },
          { loader: 'sass-loader', options: { sourceMap: true } }
        ]
      },
      {
        test: /\.sass$/,
        use: [
          isDev ? 'vue-style-loader' : MiniCSSExtractPlugin.loader,
          { loader: 'css-loader', options: { sourceMap: true } },
          { loader: 'sass-loader', options: { sourceMap: true } }
        ]
      },
      {
        test: /\.(png|jpe?g|gif)(\?.*)?$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 10000,
            name: helpers.assetsPath('img/[name].[ext]'),
            esModule: false,
          }
        }
      },
      {
        test: /\.(svg)(\?.*)?$/,
        use: {
          loader: 'file-loader',
          options: {
            limit: 10000,
            name: helpers.assetsPath('img/[name].[ext]'),
            esModule: false,
          }
        }
      },
    ]
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlPlugin({
      filename: 'index.html',
      template: 'index.html',
      inject: true
    }),
    new Dotenv({
      path: './config/.env',
      systemvars: true, // load from system env vars instead of .env file
    })
  ]
};

module.exports = webpackConfig;
