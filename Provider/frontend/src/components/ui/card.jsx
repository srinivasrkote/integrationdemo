import React from "react";
import { cn } from "./utils";

function Card({ className, children, ...props }) {
  return (
    <div
      className={cn(
        "rounded-lg border border-gray-200 bg-white shadow-sm",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

function CardHeader({ className, children, ...props }) {
  return (
    <div
      className={cn("p-6 pb-4", className)}
      {...props}
    >
      {children}
    </div>
  );
}

function CardTitle({ className, children, ...props }) {
  return (
    <h3
      className={cn("text-lg font-semibold text-gray-900", className)}
      {...props}
    >
      {children}
    </h3>
  );
}

function CardDescription({ className, children, ...props }) {
  return (
    <p
      className={cn("text-sm text-gray-600", className)}
      {...props}
    >
      {children}
    </p>
  );
}

function CardContent({ className, children, ...props }) {
  return (
    <div
      className={cn("px-6 pb-6", className)}
      {...props}
    >
      {children}
    </div>
  );
}

function CardFooter({ className, children, ...props }) {
  return (
    <div
      className={cn("flex items-center p-6 pt-0", className)}
      {...props}
    >
      {children}
    </div>
  );
}

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
};