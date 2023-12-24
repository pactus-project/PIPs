# Pactus Improvement Proposals (PIPs)

![PIP](./assets/readme/pip.png) 

The goal of the PIP project is to standardize and provide high-quality documentation for Pactus itself and conventions built upon it. This repository tracks past and ongoing improvements to Ethereum in the form of Pactus Improvement Proposals (PIPs). PIP-1 governs how PIPs are published.

The [status page](https://pips.pactus.org) tracks and lists PIPs, which can be divided into the following categories:

* Core PIPs are improvements to the Pactus consensus protocol.
* Networking PIPs specify the peer-to-peer networking layer of Pactus.
* Interface PIPs standardize interfaces to Pactus, which determine how users and applications interact with the blockchain.
* PRCs specify application layer standards, which determine how applications running on Pactus can interact with each other.
* Meta PIPs are miscellaneous improvements that nonetheless require some sort of consensus.
* Informational PIPs are non-standard improvements that do not require any form of consensus.

## Install prerequisites

1. Open Terminal.

2. Check whether you have Ruby 3.1.4 installed. Later [versions are not supported](https://stackoverflow.com/questions/14351272/undefined-method-exists-for-fileclass-nomethoderror).

   ```sh
   ruby --version
   ```

3. If you don't have Ruby installed, install Ruby 3.1.4.

4. Install Bundler:

   ```sh
   gem install bundler
   ```

5. Install dependencies:

   ```sh
   bundle install
   ```

## Build your local Jekyll site

1. Bundle assets and start the server:

   ```sh
   bundle exec jekyll serve
   ```

2. Preview your local Jekyll site in your web browser at `http://localhost:4000`.

More information on Jekyll and GitHub Pages [here](https://docs.github.com/en/enterprise/2.14/user/articles/setting-up-your-github-pages-site-locally-with-jekyll).
