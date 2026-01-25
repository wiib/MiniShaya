import type { PropsWithChildren } from "react";

interface CardProps extends PropsWithChildren {
  title?: string;
  className?: string;
}

function Card(props: CardProps) {
  return (
    <div className={`flex flex-col p-4 rounded-xl shadow ${props.className}`}>
      {props.title && <h3 className="text-xl text-center font-bold mb-2 flex-none">{props.title}</h3>}
      {props.children}
    </div>
  );
}

export default Card;
