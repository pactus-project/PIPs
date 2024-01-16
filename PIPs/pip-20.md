---
pip: 20
title: Enhanced Authentication Methodology for REST and GRPC APIs
author: Javad Rajabzadeh (@Ja7ad)
status: Draft
type: Standards
category: Interface
created: 14-01-2024
---

## Abstract

This proposal outlines the introduction of a flexible authentication mechanism that supports multiple methods for both REST and gRPC interfaces in a given system. The goal is to enhance the security layer to accommodate varying client needs including the option for no authentication, basic authentication, and API key-based authentication.

## Motivation

As systems evolve, the need for varied and robust authentication mechanisms becomes critical to cater to a range of security requirements and client capabilities. Currently, the lack of a comprehensive, flexible authentication system in our API layer limits the ability to secure communications effectively. This proposal aims to standardize the authentication process across REST and gRPC interfaces to improve security, interoperability, and ease of use.

## Specification

The proposed authentication enhancement revolves around the implementation of a middleware in the gRPC server. This middleware will intercept requests before they reach the endpoint and determine the authentication method to be applied based on the configuration specified in the TOML file. The middleware will operate as follows:

1. Inspect incoming requests for authentication credentials.
2. Validate credentials against the chosen authentication method, as detailed in the service configuration.
3. Allow access to the endpoint for valid credentials or reject it with an appropriate error message for invalid or missing credentials.

Below are the authentication control mechanisms for each supported method:

### None

When the method is set to `none`, the middleware allows all requests to pass through without any authentication checks.

### Basic Authentication

For basic authentication, the middleware extracts the `Authorization` header from the request, decodes the Base64 encoded username and password, and validates them against the credentials stored in the configuration.

### API Key Authentication

API key authentication requires the middleware to look for a predefined header (e.g., `X-Api-Key`) or query parameter in the request. The extracted key is then compared with the one specified in the configuration file.

The middleware also provides a flexible hook to integrate additional custom authentication methods in the future.

### TOML Configuration Changes

To support these features, the following configurations must be added to the TOML file:

- An authentication section with a method definition.
- Credentials' definitions for Basic and API Key methods, which the middleware will use for verification.

### Example Middleware Implementation

Here is a pseudocode example of what the middleware might look like for a gRPC server:

```go
func AuthInterceptor(authConfig AuthConfig) grpc.ServerOption {
  return grpc.UnaryInterceptor(func(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {

    // Check if authentication has been enabled
    if authConfig.Method != "none" {

      // Authenticate based on the method
      switch authConfig.Method {
      case "basic":
        // Perform basic auth check (example function call)
        if err := checkBasicAuth(ctx, authConfig.Credentials); err != nil {
          return nil, err
        }
      case "apikey":
        // Perform API key check (example function call)
        if err := checkAPIKey(ctx, authConfig.ApiKey); err != nil {
          return nil, err
        }
      default:
        // If the method is not recognized, deny the request
        return nil, status.Error(codes.Unauthenticated, "Invalid authentication method")
      }
    }

    // Call the handler if authentication was successful or not required
    return handler(ctx, req)
  })
}
```

## Rationale

The proposed authentication methods cover a broad range of use cases:

- **None** for development and testing environments where security is not a concern.
- **Basic Auth** for scenarios where simplicity and basic access control are sufficient.
- **API Key** for production environments where a single, revocable key is preferred.

This approach ensures that the system can be used in different contexts without imposing a one-size-fits-all solution.

## Backward Compatibility

The proposal ensures backward compatibility as the default method can retain 'none' for existing implementations until an explicit change is made.

## Security Considerations

Each authentication method comes with its security implications. While basic auth over SSL/TLS could be sufficient for certain cases, API keys provide a more secure alternative. However, it is essential to implement additional security measures like key rotation and HTTPS enforcement.


## Example

- Without Authentication

```toml
[grpc]
  enable = true
  listen = "[::]:50052"

  [grpc.auth]
    method = "none"

  [grpc.gateway]
    enable = true
    listen = "[::]:8080"
    enable_cors = false
```

- Basic Auth Authentication

```toml
[grpc]
  enable = true
  listen = "[::]:50052"

  [grpc.auth]
    method = "basic"
    username = "foo"
    password = "bar"

  [grpc.gateway]
    enable = true
    listen = "[::]:8080"
    enable_cors = false
```

- API Key Authentication

```toml
[grpc]
  enable = true
  listen = "[::]:50052"

  [grpc.auth]
    method = "apikey"
    key = "foobar"

  [grpc.gateway]
    enable = true
    listen = "[::]:8080"
    enable_cors = false
```
