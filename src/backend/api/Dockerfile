# Build stage
FROM mcr.microsoft.com/dotnet/sdk:10.0-preview AS build
WORKDIR /src

# Copy solution and project files
COPY AiCustomerService.Api.slnx .
COPY Directory.Build.props .
COPY src/AiCustomerService.Api/AiCustomerService.Api.csproj src/AiCustomerService.Api/
COPY tests/AiCustomerService.Api.Tests/AiCustomerService.Api.Tests.csproj tests/AiCustomerService.Api.Tests/

# Restore dependencies
RUN dotnet restore AiCustomerService.Api.slnx

# Copy all source files
COPY . .

# Build and publish
RUN dotnet publish src/AiCustomerService.Api/AiCustomerService.Api.csproj -c Release --no-restore -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0-preview AS runtime
WORKDIR /app

# Copy published output from build stage
COPY --from=build /app/publish .

# Expose port
EXPOSE 5000

# Set environment variables
ENV ASPNETCORE_URLS=http://+:5000
ENV ASPNETCORE_ENVIRONMENT=Production

# Run the application
ENTRYPOINT ["dotnet", "AiCustomerService.Api.dll"]
