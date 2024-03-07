---
pip: 20
title: Basic Authentication for gRPC APIs
author: Javad Rajabzadeh (@Ja7ad)
status: Draft
type: Standards
category: Interface
created: 14-01-2024
---

## Abstract

This proposal aims to enhance the security of gRPC APIs by implementing a Basic Authentication mechanism. The goal is to provide a simple yet effective way to authenticate clients accessing the APIs.

## Motivation

Security is paramount in modern systems, and implementing a reliable authentication mechanism is essential to safeguard sensitive data and resources. Basic Authentication offers a straightforward approach to validate client credentials and control access to gRPC services.

## Specification

The proposed authentication enhancement involves implementing a middleware component within the gRPC server to handle Basic Authentication. The middleware will intercept incoming requests, validate the provided credentials, and allow or deny access based on the authentication outcome.

### Generate by using htpasswd Apache

1. Generate Bcrypt Hash with htpasswd[^1]:
You can use the htpasswd command-line tool to generate a bcrypt-hashed password.
Here's the general syntax:

```shell
htpasswd -bnBC 10 <username> <password>
```

- -b: Use the bcrypt password encryption algorithm.
- -n: Do not update the password file.
- -B: Force bcrypt algorithm.
- -C cost: Set the cost factor for the bcrypt algorithm (higher values mean slower hashing but more secure).
- username: The username for which you want to generate the password.
- password: The password you want to hash.

For example:

```shell
htpasswd -bnBC 10 javad mypassword
```

This command will output the bcrypt-hashed password for the user javad.

2. Store the Hashed Password in Configuration File:
Once you have the bcrypt-hashed password, you can store it in your configuration file. It seems like you're using a TOML configuration file format.
In your TOML configuration file, you would include the hashed password like this:

```toml
[grpc]
  enable = true
  listen = "[::]:50052"
  auth = "javad:$2y$10$fOLKlFO0tOdSWcbMgGjbIerdF2wuaqOQd0//fNtkzpdj6LaId0rwO"  # Replace this with your username and hashed password

[grpc.gateway]
  enable = true
  listen = "[::]:8080"
  enable_cors = false
```

Replace "javad:$2y$10$fOLKlFO0tOdSWcbMgGjbIerdF2wuaqOQd0//fNtkzpdj6LaId0rwO" with the bcrypt-hashed password you generated using htpasswd.

Remember to keep your configuration file secure, especially if it contains sensitive information like passwords.

By following these steps, you can generate a bcrypt-hashed password using htpasswd and store it in your configuration file for use in your gRPC server's authentication middleware.

### Basic Authentication Middleware

The Basic Authentication middleware operates as follows:

1. Extract the `Authorization` header from incoming requests.
2. Decode the Base64-encoded username and password from the header.
3. Validate the credentials against the predefined username and password stored in the server configuration.
4. Allow access to the endpoint for valid credentials or reject the request with an appropriate error message for invalid or missing credentials.

### Example Middleware Implementation

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

Basic Authentication provides a simple yet effective way to control access to gRPC APIs. It is widely supported by client libraries and can be easily integrated into existing systems without significant overhead.

## Backward Compatibility

This proposal ensures backward compatibility by allowing existing implementations to retain their authentication method configurations. The Basic Authentication method can be selectively enabled for specific APIs or endpoints without impacting the overall system behavior.

## References

[^1]: [htpasswd - Manage user files for basic authentication](https://httpd.apache.org/docs/2.4/programs/htpasswd.html)
