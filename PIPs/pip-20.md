---
pip: 20
title: Basic Authentication for gRPC APIs
author: Javad Rajabzadeh (@Ja7ad)
status: Final
type: Standards
category: Interface
created: 14-01-2024
---

## Abstract

This proposal aims to enhance the security of gRPC APIs by implementing a Basic Authentication mechanism.
The goal is to provide a simple yet effective way to authenticate clients accessing the APIs.

## Motivation

Security is paramount in modern systems, and implementing a reliable authentication mechanism is essential to
safeguard sensitive data and resources.
Basic Authentication offers a straightforward approach to validate client credentials and
control access to gRPC services.

## Specification

The proposed authentication enhancement involves implementing a middleware component within the gRPC server to
handle Basic Authentication.
The middleware will intercept incoming requests, validate the provided credentials,
and allow or deny access based on the authentication outcome.

### Generate Password Hash

1. Generate Bcrypt Hash:

Bcrypt is a widely used hashing algorithm for securely hashing passwords.
It includes a salt to protect against rainbow table attacks and
is computationally intensive to slow down brute-force attempts.
Various methods, including the `htpasswd` command-line tool, can be used to generate a bcrypt-hashed password.
The general syntax for `htpasswd` is:

```shell
htpasswd -bnB <username> <password>
```

- `b`: Use batch mode to retrieve the password from the command line rather than prompting for it.
- `n`: Display the results on standard output.
- `B`: Force the use of the bcrypt algorithm.
- `username`: The username for which the password is being generated.
- `password`: The password to be hashed.

For example:

```shell
htpasswd -bnB foo bar
```

This command outputs the bcrypt-hashed password for the user "foo".

2. Store the Hashed Password in Configuration File:

Once the bcrypt-hashed password is obtained, it can be stored in the configuration file:

```toml
[grpc]
  enable = true
  listen = "[::]:50052"
  auth = "foo:$2y$05$3DdFhI74T5PwNyxFdh9wiOttWZCzmVEcI2GoTfNh4b1YubZgyZadS"
```

### Basic Authentication Middleware

The Basic Authentication middleware operates as follows:

1. Extract the `Authorization` header from incoming requests.
2. Decode the Base64-encoded username and password from the header.
3. Validate the credentials against the predefined username and hashed password stored in the configuration.
4. Allow access to the endpoint for valid credentials or reject the request with
   an appropriate error message for invalid or missing credentials.

#### Example Middleware Implementation

```go
func BasicAuthInterceptor(username, password string) grpc.ServerOption {
  return grpc.UnaryInterceptor(func(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {

    // Extract Authorization header from the context
    authHeader, ok := metadata.FromIncomingContext(ctx)
    if !ok {
      return nil, status.Error(codes.Unauthenticated, "Missing authentication credentials")
    }

    // Extract and decode username and password from the Authorization header
    // Perform Basic Authentication
    // If authentication fails, return an Unauthenticated error
    // If authentication succeeds, proceed to the next handler
  })
}
```

## Rationale

Basic Authentication provides a simple yet effective way to control access to gRPC APIs.
It is widely supported by client libraries and can be easily integrated into
existing systems without significant overhead.

## Backward Compatibility

This proposal ensures backward compatibility by allowing existing implementations to
retain their authentication method configurations.
The Basic Authentication method can be selectively enabled for specific APIs or
endpoints without impacting the overall system behavior.

## References

[^1]: [htpasswd - Manage user files for basic authentication](https://httpd.apache.org/docs/2.4/programs/htpasswd.html)
